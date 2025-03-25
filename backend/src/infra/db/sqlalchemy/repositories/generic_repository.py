from dataclasses import asdict
from typing import Any, Iterable, List, Optional, Type, TypeVar

from sqlalchemy import delete, func, inspect, select, text
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import class_mapper

from src.application.common.dto import Pagination
from src.application.interfaces.repositories.generic_repository import GenericRepositoryInterface
from src.domain.entities.base_entity import BaseEntity
from src.infra.db.sqlalchemy.models import Base

from .common.queries import build_bulk_update_query

Entity = TypeVar("Entity", bound=BaseEntity)


class SQLAlchemyGenericRepository(GenericRepositoryInterface[BaseEntity]):
    model_class = Type[Base]
    entity_class = Type[BaseEntity]

    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_id(self, id_: Any) -> Entity | None:
        instance = await self._session.get(self.model_class, id_)
        if instance:
            return self.model_to_entity(instance)
        return None

    async def get_first(self) -> Entity | None:
        stmt = select(self.model_class).limit(1)
        result = await self._session.scalars(stmt)
        instance = result.first()
        if instance:
            return self.model_to_entity(instance)
        return None

    async def get_list(
        self,
        limit: int = None,
        offset: int = None,
    ) -> list[Entity]:
        query = select(self.model_class)
        if offset:
            query = query.offset(offset)
        if limit:
            query = query.limit(limit)
        result = await self._session.execute(query)
        instances = result.scalars().all()
        return [self.model_to_entity(instance) for instance in instances]

    async def create(self, entity: Entity) -> Entity:
        instance = self.model_class(**asdict(entity))
        self._session.add(instance)
        await self._session.flush()
        entity.id = instance.id
        return entity

    async def update(self, entity: Entity):
        instance = self.model_class(**asdict(entity))
        await self._session.merge(instance)

    async def delete(self, entity: Entity) -> None:
        instance = self.model_class(**asdict(entity))
        await self._session.delete(instance)

    async def delete_all(self) -> None:
        await self._session.execute(delete(self.model_class))

    async def bulk_create(
        self,
        objects: list[Entity],
        ignore_conflicts: bool = False,
        batch_size: Optional[int] = None,
        update_fields: Optional[Iterable[str]] = None,
        on_conflict: Optional[Iterable[str]] = None,
    ) -> list[Entity]:
        if not objects:
            return []
        values = [self.entity_to_dict(obj) for obj in objects]
        stmt = insert(self.model_class)
        if ignore_conflicts:
            stmt = stmt.on_conflict_do_nothing()
        elif update_fields and on_conflict:
            stmt = stmt.on_conflict_do_update(
                index_elements=on_conflict,
                set_={field: getattr(stmt.excluded, field) for field in update_fields if hasattr(stmt.excluded, field)},
            )
        connection = await self._session.connection()
        if batch_size:
            [await connection.execute(stmt, values[i : i + batch_size]) for i in range(0, len(objects), batch_size)]
        else:
            await connection.execute(stmt, values)
        return objects

    async def bulk_update(
        self,
        objects: List[Entity],
        fields: Optional[Iterable[str]] = None,
        excluded_fields: Optional[Iterable[str]] = None,
        id_column: Optional[Any] = None,
        batch_size: Optional[int] = None,
    ) -> list[Entity]:
        """
        Массовое обновление записей с оптимизацией стандартного метода.
        Данная реализация использует подход с FROM VALUES WHERE
        """
        if not objects:
            return objects
        fields = set(fields) if fields else {column.name for column in inspect(self.model_class).columns}
        excluded_fields = set(excluded_fields) if excluded_fields else set()
        fields_to_update = fields - excluded_fields  # Поля для обновления

        values = [self.entity_to_dict(obj) for obj in objects]

        _query = build_bulk_update_query(
            self.model_class,
            values,
            fields_to_update,
            id_column=id_column,
        )
        query = text(_query)

        connection = await self._session.connection()
        await connection.execute(query)

        return objects

    async def in_bulk(self, id_list: list[str], field_name: str) -> dict:
        """
        Return a dictionary mapping each of the given IDs to the object with that ID.
        PostgreSQL ограничивает количество элементов в `IN` до 32 000, поэтому запрос разбивается на батчи.
        """
        if not id_list:
            return {}

        if hasattr(self.model_class, field_name):
            column = getattr(self.model_class, field_name).property.columns[0]
            if not (column.unique or column.primary_key):
                raise ValueError(f"Поле {field_name} не является уникальным в модели {self.model_class}")

        batch_size = 32_000  # Лимит PostgreSQL на кол-во аргументов
        conn = await self._session.connection()
        result_dict = {}

        for i in range(0, len(id_list), batch_size):
            batch = id_list[i : i + batch_size]
            stmt = select(self.model_class).where(getattr(self.model_class, field_name).in_(batch))
            result = await conn.execute(stmt)
            instances = result.mappings().all()

            result_dict.update({instance[field_name]: self.entity_class(**instance) for instance in instances})

        return result_dict

    def model_to_entity(self, instance: Base) -> Entity:
        """Конвертация ORM Model -> Entity"""
        instance_dict = {column.key: getattr(instance, column.key) for column in class_mapper(self.model_class).columns}
        return self.entity_class(**instance_dict)

    def dataclass_to_model(self, entity: Entity) -> Base:
        """Конвертация Entity -> ORM Model"""
        data = entity.to_dict()
        mapper = class_mapper(self.model_class)
        model_data = {col.key: data[col.key] for col in mapper.columns if col.key in data}
        return self.model_class(**model_data)

    # noinspection PyMethodMayBeStatic
    def entity_to_dict(self, entity: Entity) -> dict:
        """Конвертация Entity -> Dict"""
        return entity.to_dict()
