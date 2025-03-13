from src.application.common.dto import Pagination, PaginationResult
from src.application.interfaces.repositories.wallet import BaseWalletRepository, BaseWalletTokenRepository
from src.application.wallet.dto import GetWalletTokensFilters, WalletTokenDTO, WalletTokensPageDTO
from src.application.wallet.exceptions import WalletNotFoundException


class GetWalletTokensHandler:
    def __init__(
        self,
        wallet_repository: BaseWalletRepository,
        wallet_token_repository: BaseWalletTokenRepository,
    ) -> None:
        self._wallet_repository = wallet_repository
        self._wallet_token_repository = wallet_token_repository

    async def __call__(
        self,
        address: str,
        pagination: Pagination,
        filters: GetWalletTokensFilters,
    ) -> WalletTokensPageDTO:
        wallet = await self._wallet_repository.get_by_address(address=address)
        if not wallet:
            raise WalletNotFoundException(address)
        filter_by = filters.model_dump(exclude_none=True)
        filter_by["wallet_id"] = wallet.id
        wallet_tokens = await self._wallet_token_repository.get_page(
            pagination=pagination,
        )
        total_count = await self._wallet_token_repository.get_count(
            # filter_by=filter_by
        )
        wallet_tokens_dto = [WalletTokenDTO.from_orm(token) for token in wallet_tokens]
        return WalletTokensPageDTO(
            wallets=wallet_tokens_dto,
            pagination=PaginationResult.from_pagination(
                pagination, count=len(wallet_tokens_dto), total_count=total_count
            ),
        )
