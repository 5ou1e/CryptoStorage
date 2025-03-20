from sqlalchemy import select, update

from src.application.interfaces.repositories.flipside import BaseFlipsideAccountRepository, BaseFlipsideConfigRepository
from src.domain.entities.flipside import FlipsideAccountEntity, FlipsideConfigEntity
from src.infra.db.models.sqlalchemy import FlipsideAccount, FlipsideConfig
from src.infra.db.repositories.sqlalchemy.generic_repository import SQLAlchemyGenericRepository


class SQLAlchemyFlipsideAccountRepository(
    SQLAlchemyGenericRepository,
    BaseFlipsideAccountRepository,
):
    model_class = FlipsideAccount
    entity_class = FlipsideAccountEntity

    async def get_flipside_account(self):
        stmt = select(FlipsideAccount).where(FlipsideAccount.is_active).limit(1)
        result = await self._session.execute(stmt)
        return result.scalars().first()

    async def set_flipside_account_inactive(
        self,
        flipside_account: FlipsideAccountEntity,
    ):
        stmt = update(FlipsideAccount).where(FlipsideAccount.id == flipside_account.id).values(is_active=False)
        await self._session.execute(stmt)


class SQLAlchemyFlipsideConfigRepository(
    SQLAlchemyGenericRepository,
    BaseFlipsideConfigRepository,
):
    model_class = FlipsideConfig
    entity_class = FlipsideConfigEntity

    async def get_flipside_config(self):
        stmt = select(FlipsideConfig).limit(1)
        result = await self._session.execute(stmt)
        return result.scalars().first()
