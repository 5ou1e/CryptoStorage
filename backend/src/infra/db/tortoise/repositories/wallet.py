import logging
import math
from typing import Optional
from uuid import UUID

from tortoise.functions import Count

from src.application.interfaces.repositories.wallet import (
    WalletRepositoryInterface,
    WalletStatistic7dRepositoryInterface,
    WalletStatistic30dRepositoryInterface,
    WalletStatisticAllRepositoryInterface,
    WalletStatisticBuyPriceGt15k7dRepositoryInterface,
    WalletStatisticBuyPriceGt15k30dRepositoryInterface,
    WalletStatisticBuyPriceGt15kAllRepositoryInterface,
    WalletTokenRepositoryInterface,
)
from src.domain.entities.wallet import Wallet as WalletEntity
from src.domain.entities.wallet import WalletStatistic7d as WalletStatistic7dEntity
from src.domain.entities.wallet import WalletStatistic30d as WalletStatistic30dEntity
from src.domain.entities.wallet import WalletStatisticAll as WalletStatisticAllEntity
from src.domain.entities.wallet import WalletStatisticBuyPriceGt15k7d as WalletStatisticBuyPriceGt15k7dEntity
from src.domain.entities.wallet import WalletStatisticBuyPriceGt15k30d as WalletStatisticBuyPriceGt15k30dEntity
from src.domain.entities.wallet import WalletStatisticBuyPriceGt15kAll as WalletStatisticBuyPriceGt15kAllEntity
from src.domain.entities.wallet import WalletToken as WalletTokenEntity
from src.infra.db import queries
from src.infra.db.tortoise.models import (
    Wallet,
    WalletStatistic7d,
    WalletStatistic30d,
    WalletStatisticAll,
    WalletStatisticBuyPriceGt15k7d,
    WalletStatisticBuyPriceGt15k30d,
    WalletStatisticBuyPriceGt15kAll,
    WalletToken,
)

from .generic_repository import TortoiseGenericRepository

logger = logging.getLogger(__name__)


class TortoiseWalletStatistic7dRepository(
    TortoiseGenericRepository,
    WalletStatistic7dRepositoryInterface,
):
    model_class = WalletStatistic7d
    entity_class = WalletStatistic7dEntity


class TortoiseWalletStatistic30dRepository(
    TortoiseGenericRepository,
    WalletStatistic30dRepositoryInterface,
):
    model_class = WalletStatistic30d
    entity_class = WalletStatistic30dEntity


class TortoiseWalletStatisticAllRepository(
    TortoiseGenericRepository,
    WalletStatisticAllRepositoryInterface,
):
    model_class = WalletStatisticAll
    entity_class = WalletStatisticAllEntity


class TortoiseWalletStatisticBuyPriceGt15k7dRepository(
    TortoiseGenericRepository,
    WalletStatisticBuyPriceGt15k7dRepositoryInterface,
):
    model_class = WalletStatisticBuyPriceGt15k7d
    entity_class = WalletStatisticBuyPriceGt15k7dEntity


class TortoiseWalletStatisticBuyPriceGt15k30dRepository(
    TortoiseGenericRepository,
    WalletStatisticBuyPriceGt15k30dRepositoryInterface,
):
    model_class = WalletStatisticBuyPriceGt15k30d
    entity_class = WalletStatisticBuyPriceGt15k30dEntity


class TortoiseWalletStatisticBuyPriceGt15kAllRepository(
    TortoiseGenericRepository,
    WalletStatisticBuyPriceGt15kAllRepositoryInterface,
):
    model_class = WalletStatisticBuyPriceGt15kAll
    entity_class = WalletStatisticBuyPriceGt15kAllEntity


class TortoiseWalletTokenRepository(
    TortoiseGenericRepository,
    WalletTokenRepositoryInterface,
):
    model_class = WalletToken
    entity_class = WalletTokenEntity

    async def bulk_update_or_create_wallet_token_with_merge(
        self,
        objects: list[WalletToken],
        batch_size: Optional[int] = None,
    ) -> list[WalletToken]:
        raise NotImplementedError

    async def get_wallet_tokens_by_wallet_for_buygt15k_statistic(self, wallet_id: UUID):
        raise NotImplementedError


class TortoiseWalletRepository(
    TortoiseGenericRepository,
    WalletRepositoryInterface,
):
    model_class = Wallet
    entity_class = WalletEntity

    # noinspection PyMethodMayBeStatic
    async def get_by_address(self, address: str) -> WalletEntity | None:
        print("HELLO")
        return await Wallet.filter(address=address).first()

    async def get_wallets_for_update_stats(self, count: int = 1) -> list[WalletEntity]:
        query = queries.GET_WALLETS_FOR_UPDATE_STATS.format(count=count)
        res = await self._execute_query(query)
        return [WalletEntity(**obj) for obj in res[1] or []]

    async def get_wallets_for_buygt15k_statistic(self):
        raise NotImplementedError

    # noinspection PyMethodMayBeStatic
    async def get_wallets_by_token_addresses(
        self,
        token_addresses: list[str],
        matching_tokens_percent: int = 100,  # Мин. процент совпадающих токенов
        filter_by: Optional[dict] = None,
        prefetch: Optional[list] = None,
    ) -> list[WalletEntity]:
        # Получает кошельки, которые взаимодействовали со всеми переданными адресами токенов
        matching_tokens_percent = max(0, min(matching_tokens_percent, 100))
        wallets = (
            await Wallet.filter(
                wallet_tokens__token__address__in=token_addresses,
                _token_count__gte=math.ceil(matching_tokens_percent / 100 * len(token_addresses)),
                **filter_by,
            )
            .annotate(_token_count=Count("wallet_tokens__token_id"))  # , distinct=True
            .group_by(
                "id",
            )
            .prefetch_related(*prefetch)
            .limit(100)
        )
        return wallets
