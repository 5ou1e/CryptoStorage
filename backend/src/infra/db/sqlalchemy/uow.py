from sqlalchemy.ext.asyncio import AsyncSession

from src.application.common.interfaces.uow import UnitOfWorkInterface


class SQLAlchemyUnitOfWork(UnitOfWorkInterface):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def commit(self):
        await self._session.commit()

    async def rollback(self):
        await self._session.rollback()

    async def __aenter__(self):
        # await self._session.begin()  # Начинаем транзакцию
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            await self._session.rollback()
        else:
            await self._session.commit()
