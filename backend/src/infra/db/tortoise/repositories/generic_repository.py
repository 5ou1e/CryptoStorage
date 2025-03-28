import logging
from dataclasses import asdict
from typing import Any, Dict, Iterable, List, Optional, Sequence, TypeVar

from src.application.common.dto import Pagination
from src.application.interfaces.repositories import GenericRepositoryInterface
from src.domain.entities.base_entity import BaseEntity
from src.infra.db import queries
from src.infra.db.tortoise.repositories.utils import get_bulk_update_records_query
from tortoise import BaseDBAsyncClient, Tortoise
from tortoise.models import Model
from tortoise.queryset import QuerySet
from tortoise.transactions import in_transaction

logger = logging.getLogger(__name__)


Entity = TypeVar("Entity", bound=BaseEntity)


class TortoiseGenericRepository(GenericRepositoryInterface[BaseEntity]):
    model_class = type[Model]
    entity_class = type[BaseEntity]

    async def get_by_id(self, _id: Any) -> Entity | None:
        return await self.model_class.filter(id=_id).first()

    async def get_first(
        self,
        filter_by: Optional[dict] = None,
        order_by: Optional[list] = None,
        prefetch: Optional[list] = None,
        select_related: Optional[list] = None,
    ) -> Entity | None:
        query = self._build_query(
            filter_by=filter_by,
            order_by=order_by,
            prefetch=prefetch,
            select_related=select_related,
        )
        return await query.first()

    async def get_list(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        filter_by: Optional[dict] = None,
        order_by: Optional[list] = None,
        prefetch: Optional[list] = None,
        select_related: Optional[list] = None,
    ) -> list:
        query = self._build_query(
            filter_by=filter_by,
            order_by=order_by,
            limit=limit,
            offset=offset,
            prefetch=prefetch,
            select_related=select_related,
        )
        return await query.all()

    async def create(self, data: dict):
        return await self.model_class.create(**data)

    async def update(self, entity: Entity) -> None:
        update_data = entity.to_dict().pop("id")
        await self.model_class.filter(id=entity.id).update(**update_data)

    async def delete(self, entity: Entity):
        instance = self.model_class(**asdict(entity))
        await instance.delete()

    async def delete_all(self) -> None:
        await self.model_class.all().delete()

    async def bulk_update(
        self,
        objects: List[Entity],
        fields: Optional[Iterable[str]] = None,
        excluded_fields: Optional[Iterable[str]] = None,
        id_column: Optional[Any] = None,
        batch_size: Optional[int] = None,
        using_db: Optional[BaseDBAsyncClient] = None,
    ):
        """
        Массовое обновление записей с оптимизацией стандартного метода.
        Данная реализация использует подход с FROM VALUES WHERE
        """
        if not objects:
            return None
        fields = set(fields) if fields else set(self.model_class._meta.db_fields)
        excluded_fields = set(excluded_fields) if excluded_fields else set()
        fields_to_update = fields - excluded_fields  # Поля для обновления
        query = get_bulk_update_records_query(
            self.model_class,
            objects,
            fields_to_update,
            id_column=id_column,
        )
        return await self._execute_query(query)

    async def bulk_create(
        self,
        objects: list[Model | Entity],
        ignore_conflicts: bool = False,
        batch_size: Optional[int] = 20000,
        update_fields: Optional[Iterable[str]] = None,
        on_conflict: Optional[Iterable[str]] = None,
        using_db: Optional[BaseDBAsyncClient] = None,
    ) -> Any:
        if not objects:
            return None
        return await self.model_class.bulk_create(
            objects=objects,
            ignore_conflicts=ignore_conflicts,
            batch_size=batch_size,
            update_fields=update_fields,
            on_conflict=on_conflict,
            using_db=using_db,
        )

    # noinspection PyMethodMayBeStatic
    async def _execute_query(self, query) -> tuple[int, Sequence[dict]]:
        return await Tortoise.get_connection("default").execute_query(query)

    # noinspection PyMethodMayBeStatic
    async def _execute_query_dict(self, query) -> list[dict]:
        return await Tortoise.get_connection("default").execute_query_dict(query)

    # noinspection PyMethodMayBeStatic
    def _build_query(
        self,
        filter_by: Optional[dict] = None,
        order_by: Optional[list] = None,
        limit: int | None = None,
        offset: int | None = None,
        prefetch: Optional[list] = None,
        select_related: Optional[list] = None,
    ):
        """Применяет фильтры и сортировку к запросу, если они указаны."""
        query = self.model_class.filter()
        if filter_by:
            query = query.filter(**filter_by)
        if order_by:
            query = query.order_by(*order_by)  # Применяем сортировку, если она указана
        # Добавить префетч
        if prefetch:
            query = query.prefetch_related(*prefetch)
        if select_related:
            query = query.select_related(*select_related)
        if limit:
            query = query.limit(limit)
        if offset:
            query = query.offset(offset)
        return query
