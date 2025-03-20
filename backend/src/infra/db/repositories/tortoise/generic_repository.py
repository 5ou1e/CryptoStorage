import logging
from dataclasses import asdict
from typing import Any, Dict, Iterable, List, Optional, Sequence, TypeVar

from tortoise import BaseDBAsyncClient, Tortoise
from tortoise.models import Model
from tortoise.queryset import QuerySet
from tortoise.transactions import in_transaction

from src.application.common.dto import Pagination
from src.application.interfaces.repositories import BaseGenericRepository
from src.domain.entities.base_entity import BaseEntity
from src.infra.db import queries
from src.infra.db.repositories.tortoise.utils import get_bulk_update_records_query

logger = logging.getLogger(__name__)


Entity = TypeVar("Entity", bound=BaseEntity)


class TortoiseGenericRepository(BaseGenericRepository[BaseEntity]):
    model_class = type[Model]
    entity_class = type[BaseEntity]

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

    async def delete(self, entity: Entity):
        instance = self.model_class(**asdict(entity))
        await instance.delete()

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

    async def get_page(
        self,
        pagination: Pagination,
        filter_by: Optional[dict] = None,
        order_by: Optional[list] = None,
        prefetch: Optional[list] = None,
        select_related: Optional[list] = None,
    ) -> list:
        limit = pagination.page_size
        offset = (max(pagination.page, 1) - 1) * pagination.page_size
        return await self.get_list(
            limit=limit,
            offset=offset,
            filter_by=filter_by,
            order_by=order_by,
            prefetch=prefetch,
            select_related=select_related,
        )

    async def update(self, entity: Entity) -> None:
        update_data = asdict(entity).pop("id")
        await self.model_class.filter(id=entity.id).update(**update_data)

    async def create(self, data: dict):
        return await self.model_class.create(**data)

    # noinspection PyMethodMayBeStatic
    async def _count_estimate_with_func(self, query: QuerySet) -> int:
        """Примерное кол-во записей в таблице с фильтрацией, используя SQL-функцию"""
        async with in_transaction() as conn:
            await conn.execute_query(queries.CREATE_FUNC_COUNT_ESTIMATE)
            _query = query.sql(params_inline=True)
            safe_query = _query.replace("'", "''")  # Экранируем одиночные кавычки
            row = await conn.execute_query(queries.GET_COUNT_ESTIMATE_WITH_FUNC.format(query=safe_query))
            return int(row[1][0]["count_estimate"]) if row else 0

    async def _count_estimate_full(self) -> int:
        """Примерное кол-во записей в таблице без фильтров"""
        async with in_transaction() as conn:
            table_name = self.model_class._meta.db_table
            query = queries.GET_COUNT_ESTIMATE_FULL.format(table_name=table_name)
            result = await conn.execute_query(query)
            return result[1][0]["count_estimate"] if result else 0

    async def get_count(
        self,
        filter_by: Optional[Dict] = None,
        estimate: bool = True,
    ) -> int:
        """Метод для получения количества записей"""
        count = 0
        from tortoise.expressions import Subquery

        if estimate:
            if filter_by:
                limit = 50000
                # query = self.model_class.filter(**filter_by)
                # count = await query.limit(limit).count() # Какого-то хрена она делает SELECT без лимита
                subquery = self.model_class.filter(**filter_by).limit(limit).values("id")
                count = await self.model_class.filter(id__in=Subquery(subquery)).count()
                # count = len(await query.limit(limit).all())
                # count=1001
                if count >= limit:
                    # Если записей более limit-a, выполняем примерный подсчет
                    query = self.model_class.filter(**filter_by)
                    count = await self._count_estimate_with_func(query)
            else:
                count = await self._count_estimate_full()
        else:
            if filter_by:
                count = await self.model_class.filter(**filter_by).count()
            else:
                count = await self.model_class.all().count()
        return count

    async def bulk_update(
        self,
        objects: List[Model | Entity],
        fields: Optional[Iterable[str]] = None,
        excluded_fields: Optional[Iterable[str]] = None,
        id_column: Optional[Any] = None,
        batch_size: Optional[int] = None,
        using_db: Optional[BaseDBAsyncClient] = None,
    ):
        """
        Массовое обновление записей с оптимизацией стандартного метода.
        Данная реализация использует подход с VALUES IN вместо CASE WHEN
        """
        if not objects:
            return None
        excluded_fields = set(excluded_fields) if excluded_fields else {"created_at"}
        if not fields:
            fields = set(self.model_class._meta.db_fields)
        fields = set(fields)
        fields_to_update = list(fields - excluded_fields)  # Поля для обновления
        query = await get_bulk_update_records_query(
            self.model_class,
            objects,
            fields_to_update,
            id_column=id_column,
        )
        return await Tortoise.get_connection("default").execute_query(query)

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
