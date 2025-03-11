from dataclasses import asdict
from typing import (
    Any,
    Iterable,
    List,
    Optional,
    TypeVar,
)

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import class_mapper

from src.application.common.dto import Pagination
from src.application.interfaces.repositories.generic_repository import (
    BaseGenericRepository,
)
from src.domain.entities.base_entity import (
    BaseEntity,
)
from src.infra.db.models.sqlalchemy import Base

Entity = TypeVar("Entity", bound=BaseEntity)

# TODO: переделать маппинг сущностей


class SQLAlchemyGenericRepository(BaseGenericRepository[BaseEntity]):
    model_class = type[Base]
    entity_class = type[BaseEntity]

    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_id(self, id_: Any) -> Entity | None:
        instance = await self._session.get(self.model_class, id_)
        return self.instance_to_entity(instance)

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
        return [self.instance_to_entity(instance) for instance in instances]

    async def get_page(self, pagination: Pagination) -> list[Entity]:
        offset = (max(pagination.page, 1) - 1) * pagination.page_size
        return await self.get_list(limit=pagination.page_size, offset=offset)

    async def get_count(self) -> int:
        query = select(func.count()).select_from(self.model_class)
        result = await self._session.execute(query)
        return result.scalar()

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

    async def bulk_create(
        self,
        objects: list[Entity],
        ignore_conflicts: bool = False,
        batch_size: Optional[int] = None,
        update_fields: Optional[Iterable[str]] = None,
        on_conflict: Optional[Iterable[str]] = None,
    ) -> Any:
        if not objects:
            return None
        values = [asdict(obj) for obj in objects]
        stmt = insert(self.model_class)
        if ignore_conflicts:
            stmt = stmt.on_conflict_do_nothing()
        elif update_fields and on_conflict:
            stmt = stmt.on_conflict_do_update(
                index_elements=on_conflict,
                set_={field: getattr(stmt.excluded, field) for field in update_fields if hasattr(stmt.excluded, field)},
            )
        await self._session.execute(stmt, values)

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
        Данная реализация использует подход с VALUES IN вместо CASE WHEN
        """
        raise NotImplementedError
        # if not objects:
        #     return objects
        # excluded_fields = set(excluded_fields) if excluded_fields else {"created_at"}
        # if not fields:
        #     fields = {column.name for column in inspect(self.model_class).columns}
        # fields = set(fields)
        # fields_to_update = list(fields - excluded_fields)  # Поля для обновления
        # query = bulk_update_records_query(
        #     self.model_class,
        #     objects,
        #     fields_to_update,
        #     id_column=id_column,
        # )
        # await self._session.execute(query)
        # return objects

    def instance_to_entity(self, instance: model_class) -> Entity:
        instance_dict = {
            column.key: getattr(instance, column.key) for column in class_mapper(instance.__class__).columns
        }
        return self.entity_class(**instance_dict)
