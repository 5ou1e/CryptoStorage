from src.application.common.dto import Pagination, PaginationResult
from src.application.interfaces.repositories.wallet import BaseWalletRepository
from src.application.wallet.dto import GetWalletsFilters, WalletDTO, WalletsPageDTO


class GetWalletsHandler:
    def __init__(
        self,
        wallet_repository: BaseWalletRepository,
    ) -> None:
        self._wallet_repository = wallet_repository

    async def __call__(
        self,
        pagination: Pagination,
        filters: GetWalletsFilters,
    ) -> WalletsPageDTO:
        wallets = await self._wallet_repository.get_page(
            pagination=pagination,
            # filters=filters
        )
        total_count = await self._wallet_repository.get_count(
            # filters=filters
        )
        wallets_dto = [WalletDTO.from_orm(wallet) for wallet in wallets]

        return WalletsPageDTO(
            wallets=wallets_dto,
            pagination=PaginationResult.from_pagination(pagination, count=len(wallets), total_count=total_count),
        )
