from src.application.common.dto import Pagination
from src.application.common.interfaces.readers import WalletReaderInterface
from src.application.handlers.wallet.dto import GetWalletTokensFilters, WalletTokensPageDTO
from src.application.handlers.wallet.dto.wallet_token import GetWalletTokensSorting


class GetWalletTokensHandler:
    def __init__(self, wallet_reader: WalletReaderInterface) -> None:
        self._reader = wallet_reader

    async def __call__(
        self,
        address: str,
        pagination: Pagination,
        filters: GetWalletTokensFilters,
        sorting: GetWalletTokensSorting,
    ) -> WalletTokensPageDTO:
        return await self._reader.get_wallet_tokens(address, pagination=pagination, filters=filters, sorting=sorting)
