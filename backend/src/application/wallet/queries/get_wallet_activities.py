from src.application.common.dto import Pagination, PaginationResult
from src.application.interfaces.repositories.swap import BaseSwapRepository
from src.application.interfaces.repositories.wallet import BaseWalletRepository
from src.application.wallet.dto import GetWalletActivitiesFilters, WalletActivitiesPageDTO, WalletActivityDTO
from src.application.wallet.exceptions import WalletNotFoundException


class GetWalletActivitiesHandler:
    def __init__(
        self,
        wallet_repository: BaseWalletRepository,
        swap_repository: BaseSwapRepository,
    ) -> None:
        self._wallet_repository = wallet_repository
        self._swap_repository = swap_repository

    async def __call__(
        self,
        address,
        pagination: Pagination,
        filters: GetWalletActivitiesFilters,
    ) -> WalletActivitiesPageDTO:
        wallet = await self._wallet_repository.get_by_address(address=address)
        if not wallet:
            raise WalletNotFoundException(address)
        filter_by = filters.model_dump(exclude_none=True)
        filter_by["wallet_id"] = wallet.id
        activities = await self._swap_repository.get_page(
            pagination=pagination,
        )
        total_count = await self._swap_repository.get_count(
            # filter_by=filter_by
        )
        wallet_activities_dto = [WalletActivityDTO.from_orm(activity) for activity in activities]
        return WalletActivitiesPageDTO(
            wallets=wallet_activities_dto,
            pagination=PaginationResult.from_pagination(
                pagination, count=len(wallet_activities_dto), total_count=total_count
            ),
        )
