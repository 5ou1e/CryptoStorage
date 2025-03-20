from abc import ABC, abstractmethod
from typing import Optional

from src.application.interfaces.repositories.generic_repository import BaseGenericRepository
from src.domain.entities.wallet import (
    WalletEntity,
    WalletStatistic7dEntity,
    WalletStatistic30dEntity,
    WalletStatisticAllEntity,
    WalletStatisticBuyPriceGt15k7dEntity,
    WalletStatisticBuyPriceGt15k30dEntity,
    WalletStatisticBuyPriceGt15kAllEntity,
)


class BaseWalletStatistic7dRepository(
    BaseGenericRepository[WalletStatistic7dEntity],
    ABC,
):
    pass


class BaseWalletStatistic30dRepository(
    BaseGenericRepository[WalletStatistic30dEntity],
    ABC,
):
    pass


class BaseWalletStatisticAllRepository(
    BaseGenericRepository[WalletStatisticAllEntity],
    ABC,
):
    pass


class BaseWalletStatisticBuyPriceGt15k7dRepository(
    BaseGenericRepository[WalletStatisticBuyPriceGt15k7dEntity],
    ABC,
):
    pass


class BaseWalletStatisticBuyPriceGt15k30dRepository(
    BaseGenericRepository[WalletStatisticBuyPriceGt15k30dEntity],
    ABC,
):
    pass


class BaseWalletStatisticBuyPriceGt15kAllRepository(
    BaseGenericRepository[WalletStatisticBuyPriceGt15kAllEntity],
    ABC,
):
    pass


class BaseWalletTokenRepository(BaseGenericRepository[WalletEntity], ABC):
    pass


class BaseWalletRepository(BaseGenericRepository[WalletEntity], ABC):

    @abstractmethod
    async def get_by_address(self, address: str) -> WalletEntity | None:
        raise NotImplementedError

    @abstractmethod
    async def get_by_address_with_details_and_stats(self, address: str) -> WalletEntity | None:
        raise NotImplementedError

    @abstractmethod
    async def get_wallets_for_update_stats(self, count: int = 1) -> list[WalletEntity]:
        raise NotImplementedError

    @abstractmethod
    async def get_wallets_by_token_addresses(
        self,
        token_addresses: list[str],
        matching_tokens_percent: int = 100,  # Мин. процент совпадающих токенов
        filter_by: Optional[dict] = None,
        prefetch: Optional[list] = None,
    ) -> list[WalletEntity]:
        # Получает кошельки, которые взаимодействовали со всеми переданными адресами токенов
        raise NotImplementedError
