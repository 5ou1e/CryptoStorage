from typing import Optional

from sqlalchemy import func, select, text
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select

from src.application.common.dto import Pagination
from src.application.interfaces.readers.generic_reader import GenericReaderInterface
from src.infra.db import queries


class SQLAlchemyGenericReader(GenericReaderInterface):

    def __init__(self, session: AsyncSession):
        self._session = session

    def _get_limit_offset_from_pagination(self, pagination: Pagination):  # noqa
        offset = (max(pagination.page, 1) - 1) * pagination.page_size
        limit = pagination.page_size
        return limit, offset

    async def _get_count(self, query: Select, estimate: bool = True, limit_for_estimate: Optional[int] = None) -> int:
        """Получает количество записей для переданного запроса SQLAlchemy"""
        if estimate:
            limit = limit_for_estimate if limit_for_estimate is not None else 1000
            # subquery = query.limit(limit).with_only_columns(query.selected_columns[0])
            # subquery_result = await self._session.execute(subquery)
            # count = len(subquery_result.scalars().all())
            count = 100000
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
