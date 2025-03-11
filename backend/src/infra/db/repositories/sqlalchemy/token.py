from sqlalchemy import select

from src.application.interfaces.repositories.token import (
    BaseTokenPriceRepository,
    BaseTokenRepository,
)
from src.domain.entities.token import (
    TokenEntity,
    TokenPriceEntity,
)
from src.infra.db.models.sqlalchemy.token import (
    Token,
    TokenPrice,
)

from .generic_repository import (
    SQLAlchemyGenericRepository,
)


class SQLAlchemyTokenRepository(
    SQLAlchemyGenericRepository,
    BaseTokenRepository,
):
    model_class = Token
    entity_class = TokenEntity

    # noinspection PyMethodMayBeStatic
    async def get_by_address(self, address: str) -> Token | None:
        stmt = select(self.model_class).where(self.model_class.address == address)
        result = await self._session.execute(stmt)
        return result.scalars().first()


class SQLAlchemyTokenPriceRepository(
    SQLAlchemyGenericRepository,
    BaseTokenPriceRepository,
):
    model_class = TokenPrice
    entity_class = TokenPriceEntity
