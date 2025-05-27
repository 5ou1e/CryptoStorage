from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from src.application.common.interfaces.repositories.generic_repository import GenericRepositoryInterface
from src.domain.entities.wallet import (
    Wallet,
    WalletStatistic7d,
    WalletStatistic30d,
    WalletStatisticAll,
    WalletStatisticBuyPriceGt15k7d,
    WalletStatisticBuyPriceGt15k30d,
    WalletStatisticBuyPriceGt15kAll,
    WalletToken,
)


class WalletStatistic7dRepositoryInterface(
    GenericRepositoryInterface[WalletStatistic7d],
    ABC,
):
    pass


class WalletStatistic30dRepositoryInterface(
    GenericRepositoryInterface[WalletStatistic30d],
    ABC,
):
    pass


class WalletStatisticAllRepositoryInterface(
    GenericRepositoryInterface[WalletStatisticAll],
    ABC,
):
    pass


class WalletStatisticBuyPriceGt15k7dRepositoryInterface(
    GenericRepositoryInterface[WalletStatisticBuyPriceGt15k7d],
    ABC,
):
    pass


class WalletStatisticBuyPriceGt15k30dRepositoryInterface(
    GenericRepositoryInterface[WalletStatisticBuyPriceGt15k30d],
    ABC,
):
    pass


class WalletStatisticBuyPriceGt15kAllRepositoryInterface(
    GenericRepositoryInterface[WalletStatisticBuyPriceGt15kAll],
    ABC,
):
    pass


class WalletTokenRepositoryInterface(GenericRepositoryInterface[WalletToken], ABC):

    @abstractmethod
    async def get_wallet_tokens_by_wallets_list(self, wallet_ids: list[UUID]):
        raise NotImplementedError

    @abstractmethod
    async def get_wallet_tokens_by_wallets_list_for_buygt15k_statistic(
        self, wallet_ids: list[UUID]
    ) -> list[WalletToken]:
        raise NotImplementedError

    @abstractmethod
    async def bulk_update_or_create_wallet_token_with_merge(
        self,
        objects: list[WalletToken],
        batch_size: Optional[int] = None,
    ) -> list[WalletToken]:
        raise NotImplementedError


class WalletRepositoryInterface(GenericRepositoryInterface[Wallet], ABC):

    @abstractmethod
    async def get_by_address(self, address: str) -> Wallet | None:
        raise NotImplementedError

    @abstractmethod
    async def get_wallets_for_update_stats(self, count: int = 1) -> list[Wallet]:
        raise NotImplementedError

    @abstractmethod
    async def get_wallets_for_buygt15k_statistic(self) -> list[Wallet]:
        raise NotImplementedError

    @abstractmethod
    async def get_wallets_by_token_addresses(
        self,
        token_addresses: list[str],
        matching_tokens_percent: int = 100,  # Мин. процент совпадающих токенов
        filter_by: Optional[dict] = None,
        prefetch: Optional[list] = None,
    ) -> list[Wallet]:
        # Получает кошельки, которые взаимодействовали со всеми переданными адресами токенов
        raise NotImplementedError
