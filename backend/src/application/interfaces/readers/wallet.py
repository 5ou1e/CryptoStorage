from abc import ABC, abstractmethod

from src.application.common.dto import Pagination
from src.application.wallet.dto import (
    WalletActivitiesPageDTO,
    WalletDTO,
    WalletsPageDTO,
    WalletTokensPageDTO,
    GetWalletsFilters,
)
from src.application.wallet.dto.wallet import GetWalletsSorting
from src.application.wallet.dto.wallet_activity import GetWalletActivitiesSorting, GetWalletActivitiesFilters
from src.application.wallet.dto.wallet_token import GetWalletTokensSorting, GetWalletTokensFilters


class WalletReaderInterface(ABC):

    @abstractmethod
    async def get_wallets(
        self, pagination: Pagination, filters: GetWalletsFilters, sorting: GetWalletsSorting
    ) -> WalletsPageDTO:
        raise NotImplementedError

    @abstractmethod
    async def get_wallet_by_address(self, address: str) -> WalletDTO:
        raise NotImplementedError

    @abstractmethod
    async def get_wallet_activities(
        self,
        address: str,
        pagination: Pagination,
        filters: GetWalletActivitiesFilters,
        sorting: GetWalletActivitiesSorting,
    ) -> WalletActivitiesPageDTO:
        raise NotImplementedError

    @abstractmethod
    async def get_wallet_tokens(
        self,
        address: str,
        pagination: Pagination,
        filters: GetWalletTokensFilters,
        sorting: GetWalletTokensSorting,
    ) -> WalletTokensPageDTO:
        raise NotImplementedError
