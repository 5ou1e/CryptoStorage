from sqlalchemy import select, update

from src.application.interfaces.repositories.flipside import (
    FlipsideAccountRepositoryInterface,
    FlipsideConfigRepositoryInterface,
)
from src.domain.entities.flipside import FlipsideAccount as FlipsideAccountEntity
from src.domain.entities.flipside import FlipsideConfig as FlipsideConfigEntity
from src.infra.db.sqlalchemy.models import FlipsideAccount, FlipsideConfig
from src.infra.db.sqlalchemy.repositories.generic_repository import (
    SQLAlchemyGenericRepository,
)


class SQLAlchemyFlipsideAccountRepositoryInterface(
    SQLAlchemyGenericRepository,
    FlipsideAccountRepositoryInterface,
):
    model_class = FlipsideAccount
    entity_class = FlipsideAccountEntity

    async def get_first_active(self) -> FlipsideAccountEntity:
        stmt = select(FlipsideAccount).where(FlipsideAccount.is_active).limit(1)
        result = await self._session.execute(stmt)
        return result.scalars().first()

    async def set_flipside_account_inactive(
        self,
        flipside_account: FlipsideAccount,
    ) -> None:
        stmt = update(FlipsideAccount).where(FlipsideAccount.id == flipside_account.id).values(is_active=False)
        await self._session.execute(stmt)


class SQLAlchemyFlipsideConfigRepositoryInterface(
    SQLAlchemyGenericRepository,
    FlipsideConfigRepositoryInterface,
):
    model_class = FlipsideConfig
    entity_class = FlipsideConfigEntity

    async def update_swaps_parsed_until_timestamp(self, entity: FlipsideConfigEntity) -> None:
        stmt = (
            update(self.model_class)
            .where(self.model_class.id == entity.id)
            .values(swaps_parsed_until_block_timestamp=entity.swaps_parsed_until_block_timestamp)
        )
        await self._session.execute(stmt)
