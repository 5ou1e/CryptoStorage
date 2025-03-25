from abc import ABC, abstractmethod

from src.application.common.dto import Pagination
from src.application.token.dto import TokenDTO, TokensPageDTO


class TokenReaderInterface(ABC):

    @abstractmethod
    async def get_tokens(self, pagination: Pagination) -> TokensPageDTO:
        raise NotImplementedError

    @abstractmethod
    async def get_token_by_address(self, address: str) -> TokenDTO:
        raise NotImplementedError
