from typing import Optional, Type

from pydantic import BaseModel
from sqlalchemy import func, select, text
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select

from src.infra.db import queries
from dataclass_sqlalchemy_mixins.base import utils as dsm_utils

from src.infra.db.sqlalchemy.models import Base


class SQLAlchemyBaseReader:

    def __init__(self, session: AsyncSession):
        self._session = session

    def _apply_filters_sorting_limit_offset(
        self,
        query,
        model: Type[Base],
        filters: BaseModel,
        sorting: BaseModel,
        limit: int,
        offset: int
    ):
        # Применяем фильтры
        query = count_query = dsm_utils.apply_filters(query=query, filters=filters.model_dump(exclude_none=True), model=model)
        # Применяем сортировку, если она есть
        if order_by := sorting.order_by:
            query = dsm_utils.apply_order_by(query=query, order_by=order_by, model=model)
        # Применяем пагинацию
        if limit:
            query = query.limit(limit)
        if offset:
            query = query.offset(offset)

        return query, count_query

    async def _get_count(self, query: Select, estimate: bool = True, limit_for_estimate: Optional[int] = None) -> int:
        """Получает количество записей для переданного запроса SQLAlchemy"""
        if estimate:
            limit = limit_for_estimate if limit_for_estimate is not None else 1000
            subquery = query.limit(limit).with_only_columns(query.selected_columns[0])
            subquery_result = await self._session.execute(subquery)
            count = len(subquery_result.scalars().all())
            if count >= limit:
                # TODO Убрать CREATE_FUNC_COUNT_ESTIMATE в конфигурацию, чтобы не вызывать создание каждый запрос
                await self._session.execute(text(queries.CREATE_FUNC_COUNT_ESTIMATE))
                compiled_query = query.compile(compile_kwargs={"literal_binds": True}, dialect=postgresql.dialect())
                query_string = str(compiled_query)
                query_string = query_string.replace("'", "''")  # Экранируем одинарные кавычки
                estimate_query = queries.GET_COUNT_ESTIMATE_WITH_FUNC.format(query=query_string)
                result = await self._session.execute(text(estimate_query))
                count = result.scalar() or count
        else:
            count_query = select(func.count()).select_from(query.subquery())
            result = await self._session.execute(count_query)
            count = result.scalar() or 0

        return count
