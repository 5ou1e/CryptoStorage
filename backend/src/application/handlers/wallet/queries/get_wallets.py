from src.application.common.dto import Pagination
from src.application.common.interfaces.readers import WalletReaderInterface
from src.application.handlers.wallet.dto import GetWalletsFilters, WalletsPageDTO
from src.application.handlers.wallet.dto.wallet import GetWalletsSorting


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
        sorting: GetWalletsSorting,
    ) -> WalletsPageDTO:
        return await self._reader.get_wallets(pagination, filters, sorting)
