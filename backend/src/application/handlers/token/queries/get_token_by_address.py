from src.application.common.interfaces.readers import TokenReaderInterface
from src.application.handlers.token.dto import TokenDTO


class GetTokenByAddressHandler:
    def __init__(
        self,
        token_reader: TokenReaderInterface,
    ) -> None:
        self._reader = token_reader

    async def __call__(self, address: str) -> TokenDTO:
        return await self._reader.get_token_by_address(address)
