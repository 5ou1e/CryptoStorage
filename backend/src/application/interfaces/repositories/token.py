from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID

from src.application.interfaces.repositories.generic_repository import (
    GenericRepositoryInterface,
)
from src.domain.entities.token import Token, TokenPrice


class TokenRepositoryInterface(GenericRepositoryInterface[Token], ABC):
    """Интерфейс репозитория Token"""

    @abstractmethod
    async def get_by_address(self, address: str) -> Token | None:
        raise NotImplementedError

    @abstractmethod
    async def get_tokens_without_metadata(self, limit=100) -> list[Token]:
        raise NotImplemented


class TokenPriceRepositoryInterface(GenericRepositoryInterface[TokenPrice], ABC):
    """Интерфейс репозитория Token-price"""

    @abstractmethod
    async def get_latest_by_token(self, token_id: str) -> TokenPrice | None:
        raise NotImplementedError

    @abstractmethod
    async def get_prices_by_token(
        self, token_id: UUID, minute_from: datetime, minute_to: datetime
    ) -> list[TokenPrice]:
        raise NotImplementedError
