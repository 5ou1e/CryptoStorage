from src.application.common.dto import Pagination
from src.application.interfaces.readers import TokenReaderInterface
from src.application.token.dto import GetTokensFilters, TokensPageDTO


class GetTokensHandler:
    def __init__(
        self,
        token_reader: TokenReaderInterface,
    ):
        self._reader = token_reader

    async def __call__(
        self,
        pagination: Pagination,
        filters: GetTokensFilters,
    ) -> TokensPageDTO:
        return await self._reader.get_tokens(pagination=pagination)
