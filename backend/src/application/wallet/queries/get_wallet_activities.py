from src.application.common.dto import Pagination
from src.application.interfaces.readers import WalletReaderInterface
from src.application.wallet.dto import (
    GetWalletActivitiesFilters,
    WalletActivitiesPageDTO,
)


class GetWalletActivitiesHandler:
    def __init__(self, wallet_reader: WalletReaderInterface) -> None:
        self._reader = wallet_reader

    async def __call__(
        self,
        address,
        pagination: Pagination,
        filters: GetWalletActivitiesFilters,
    ) -> WalletActivitiesPageDTO:
        return await self._reader.get_wallet_activities(
            address=address, pagination=pagination
        )
