from abc import ABC, abstractmethod

from src.application.common.dto import Pagination
from src.application.handlers.wallet.dto import (
    GetWalletsFilters,
    WalletActivitiesPageDTO,
    WalletDTO,
    WalletsPageDTO,
    WalletTokensPageDTO,
)
from src.application.handlers.wallet.dto.wallet import GetWalletsSorting
from src.application.handlers.wallet.dto.wallet_activity import GetWalletActivitiesFilters, GetWalletActivitiesSorting
from src.application.handlers.wallet.dto.wallet_token import GetWalletTokensFilters, GetWalletTokensSorting


class WalletReaderInterface(ABC):

    @abstractmethod
    async def get_wallets(
        self,
        pagination: Pagination,
        filters: GetWalletsFilters,
        sorting: GetWalletsSorting,
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
