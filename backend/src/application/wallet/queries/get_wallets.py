from src.application.common.dto import Pagination
from src.application.interfaces.readers import WalletReaderInterface
from src.application.wallet.dto import GetWalletsFilters, WalletsPageDTO


class GetWalletsHandler:
    def __init__(
        self,
        wallet_reader: WalletReaderInterface,
    ) -> None:
        self._reader = wallet_reader

    async def __call__(
        self,
        pagination: Pagination,
        filters: GetWalletsFilters,
    ) -> WalletsPageDTO:
        return await self._reader.get_wallets(pagination)
