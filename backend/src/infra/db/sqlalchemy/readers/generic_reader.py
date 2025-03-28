from sqlalchemy import func, select, text
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select
from src.application.interfaces.readers.generic_reader import GenericReaderInterface
from src.infra.db import queries


class SQLAlchemyGenericReader(GenericReaderInterface):

    def __init__(self, session: AsyncSession):
        self._session = session

    async def _get_count_for_query(
        self, query: Select, estimate: bool = True, limit_for_estimate=None
    ) -> int:
        """Получает количество записей для переданного запроса SQLAlchemy"""
        if estimate:
            limit = limit_for_estimate if limit_for_estimate is not None else 50000
            subquery = query.limit(limit).with_only_columns(query.selected_columns[0])
            subquery_result = await self._session.execute(subquery)
            count = len(subquery_result.scalars().all())

            if count >= limit:
                # table_name = query.column_descriptions[0]["entity"].__tablename__
                # estimate_query = select(func.reltuples(text(table_name))).select_from(text(table_name))
                # result = await self._session.execute(estimate_query)
                # count = result.scalar() or count  # Если estimate не сработал, используем count из лимита
                # TODO Убрать это в конфигурацию, чтобы не вызывать создание каждый запрос
                await self._session.execute(text(queries.CREATE_FUNC_COUNT_ESTIMATE))
                compiled_query = query.compile(
                    compile_kwargs={"literal_binds": True}, dialect=postgresql.dialect()
                )
                query_string = str(compiled_query)
                query_string = query_string.replace(
                    "'", "''"
                )  # Экранируем одинарные кавычки
                estimate_query = queries.GET_COUNT_ESTIMATE_WITH_FUNC.format(
                    query=query_string
                )
                result = await self._session.execute(text(estimate_query))
                count = result.scalar() or count
        else:
            count_query = select(func.count()).select_from(query.subquery())
            result = await self._session.execute(count_query)
            count = result.scalar() or 0

        return count
