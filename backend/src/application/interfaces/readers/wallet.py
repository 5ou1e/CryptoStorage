from abc import ABC, abstractmethod

from src.application.common.dto import Pagination
from src.application.wallet.dto import (
    WalletActivitiesPageDTO,
    WalletDTO,
    WalletsPageDTO,
    WalletTokensPageDTO,
)


class WalletReaderInterface(ABC):

    @abstractmethod
    async def get_wallets(self, pagination: Pagination) -> WalletsPageDTO:
        raise NotImplementedError

    @abstractmethod
    async def get_wallet_by_address(self, address: str) -> WalletDTO:
        raise NotImplementedError

    @abstractmethod
    async def get_wallet_activities(
        self, address: str, pagination: Pagination
    ) -> WalletActivitiesPageDTO:
        raise NotImplementedError

    @abstractmethod
    async def get_wallet_tokens(
        self, address: str, pagination: Pagination
    ) -> WalletTokensPageDTO:
        raise NotImplementedError
