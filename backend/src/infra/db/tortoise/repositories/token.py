from src.application.interfaces.repositories.token import (
    TokenPriceRepositoryInterface,
    TokenRepositoryInterface,
)
from src.domain.entities.token import Token as TokenEntity
from src.domain.entities.token import TokenPrice as TokenPriceEntity
from src.infra.db.tortoise.models.token import Token, TokenPrice

from .generic_repository import TortoiseGenericRepository


class TortoiseTokenRepository(TortoiseGenericRepository, TokenRepositoryInterface):
    model_class = Token
    entity_class = TokenEntity

    # noinspection PyMethodMayBeStatic
    async def get_by_address(self, address: str) -> TokenEntity | None:
        return await Token.filter(address=address).first()


class TortoiseTokenPriceRepository(
    TortoiseGenericRepository,
    TokenPriceRepositoryInterface,
):
    model_class = TokenPrice
    entity_class = TokenPriceEntity
