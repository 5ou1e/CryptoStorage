from src.application.common.dto import Pagination
from src.application.interfaces.readers import WalletReaderInterface
from src.application.wallet.dto import GetWalletTokensFilters, WalletTokensPageDTO


class GetWalletTokensHandler:
    def __init__(self, wallet_reader: WalletReaderInterface) -> None:
        self._reader = wallet_reader

    async def __call__(
        self,
        address: str,
        pagination: Pagination,
        filters: GetWalletTokensFilters,
    ) -> WalletTokensPageDTO:
        return await self._reader.get_wallet_tokens(address, pagination=pagination)
