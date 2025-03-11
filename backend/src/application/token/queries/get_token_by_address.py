from src.application.interfaces.repositories import (
    BaseTokenRepository,
)
from src.application.token.dto import TokenDTO
from src.application.token.exceptions import (
    TokenNotFoundException,
)


class GetTokenByAddressHandler:
    def __init__(
        self,
        token_repository: BaseTokenRepository,
    ) -> None:
        self._token_repository = token_repository

    async def __call__(self, address: str) -> TokenDTO:
        token = await self._token_repository.get_by_address(address=address)
        if not token:
            raise TokenNotFoundException(address)
        return TokenDTO.from_orm(token)
