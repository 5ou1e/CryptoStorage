from datetime import datetime
from uuid import UUID

from sqlalchemy import select

from src.application.interfaces.repositories.token import (
    TokenPriceRepositoryInterface,
    TokenRepositoryInterface,
)
from src.application.token.exceptions import TokenNotFoundException
from src.domain.entities.token import Token as TokenEntity
from src.domain.entities.token import TokenPrice as TokenPriceEntity
from src.infra.db.sqlalchemy.models.token import Token, TokenPrice

from .generic_repository import SQLAlchemyGenericRepository


class SQLAlchemyTokenRepository(
    SQLAlchemyGenericRepository,
    TokenRepositoryInterface,
):
    model_class = Token
    entity_class = TokenEntity

    # noinspection PyMethodMayBeStatic
    async def get_by_address(self, address: str) -> TokenEntity | None:
        stmt = select(self.model_class).where(self.model_class.address == address)
        result = await self._session.scalars(stmt)
        instance = result.first()
        if not instance:
            raise TokenNotFoundException(address)
        return self.model_to_entity(instance)

    async def get_tokens_with_no_metadata_parsed(self, limit=100) -> list[TokenEntity]:
        stmt = select(self.model_class).where(self.model_class.is_metadata_parsed == False).limit(limit)
        result = await self._session.execute(stmt)
        instances = result.scalars().all()  # Получаем список объектов Token
        return [self.model_to_entity(instance) for instance in instances]

    async def bulk_update_all_metadata_fields(self, tokens: list[TokenEntity]) -> None:
        await self.bulk_update(
            tokens,
            fields=["name", "symbol", "uri", "logo", "created_on", "is_metadata_parsed", "updated_at"],
        )


class SQLAlchemyTokenPriceRepository(
    SQLAlchemyGenericRepository,
    TokenPriceRepositoryInterface,
):
    model_class = TokenPrice
    entity_class = TokenPriceEntity

    async def get_latest_by_token(self, token_id: UUID) -> TokenPriceEntity | None:
        """Возвращает последнюю по времени цену по id токена"""
        query = select(TokenPrice).where(TokenPrice.token_id == token_id).order_by(TokenPrice.minute.desc()).limit(1)
        result = await self._session.scalars(query)
        instance = result.first()
        if not instance:
            return None
        return self.model_to_entity(instance)

    async def get_prices_by_token(
        self, token_id: UUID, minute_from: datetime, minute_to: datetime
    ) -> list[TokenPriceEntity]:
        query = select(self.model_class).where(
            self.model_class.token_id == token_id,
            TokenPrice.minute >= minute_from,
            TokenPrice.minute <= minute_to,
        )
        result = await self._session.scalars(query)
        instances = result.all()
        prices = [self.model_to_entity(instance) for instance in instances]
        return prices
