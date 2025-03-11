import logging
import math
from typing import Optional

from tortoise.functions import Count

from src.application.interfaces.repositories.wallet import (
    BaseWalletDetailRepository,
    BaseWalletRepository,
    BaseWalletStatistic7dRepository,
    BaseWalletStatistic30dRepository,
    BaseWalletStatisticAllRepository,
    BaseWalletStatisticBuyPriceGt15k7dRepository,
    BaseWalletStatisticBuyPriceGt15k30dRepository,
    BaseWalletStatisticBuyPriceGt15kAllRepository,
    BaseWalletTokenRepository,
)
from src.domain.entities.wallet import (
    WalletDetailEntity,
    WalletEntity,
    WalletStatistic7dEntity,
    WalletStatistic30dEntity,
    WalletStatisticAllEntity,
    WalletStatisticBuyPriceGt15k7dEntity,
    WalletStatisticBuyPriceGt15k30dEntity,
    WalletStatisticBuyPriceGt15kAllEntity,
    WalletTokenEntity,
)
from src.infra.db import queries
from src.infra.db.models.tortoise import (
    Wallet,
    WalletDetail,
    WalletStatistic7d,
    WalletStatistic30d,
    WalletStatisticAll,
    WalletStatisticBuyPriceGt15k7d,
    WalletStatisticBuyPriceGt15k30d,
    WalletStatisticBuyPriceGt15kAll,
    WalletToken,
)

from .generic_repository import (
    TortoiseGenericRepository,
)

logger = logging.getLogger(__name__)


class TortoiseWalletDetailRepository(
    TortoiseGenericRepository,
    BaseWalletDetailRepository,
):
    model_class = WalletDetail
    entity_class = WalletDetailEntity


class TortoiseWalletStatistic7dRepository(
    TortoiseGenericRepository,
    BaseWalletStatistic7dRepository,
):
    model_class = WalletStatistic7d
    entity_class = WalletStatistic7dEntity


class TortoiseWalletStatistic30dRepository(
    TortoiseGenericRepository,
    BaseWalletStatistic30dRepository,
):
    model_class = WalletStatistic30d
    entity_class = WalletStatistic30dEntity


class TortoiseWalletStatisticAllRepository(
    TortoiseGenericRepository,
    BaseWalletStatisticAllRepository,
):
    model_class = WalletStatisticAll
    entity_class = WalletStatisticAllEntity


class TortoiseWalletStatisticBuyPriceGt15k7dRepository(
    TortoiseGenericRepository,
    BaseWalletStatisticBuyPriceGt15k7dRepository,
):
    model_class = WalletStatisticBuyPriceGt15k7d
    entity_class = WalletStatisticBuyPriceGt15k7dEntity


class TortoiseWalletStatisticBuyPriceGt15k30dRepository(
    TortoiseGenericRepository,
    BaseWalletStatisticBuyPriceGt15k30dRepository,
):
    model_class = WalletStatisticBuyPriceGt15k30d
    entity_class = WalletStatisticBuyPriceGt15k30dEntity


class TortoiseWalletStatisticBuyPriceGt15kAllRepository(
    TortoiseGenericRepository,
    BaseWalletStatisticBuyPriceGt15kAllRepository,
):
    model_class = WalletStatisticBuyPriceGt15kAll
    entity_class = WalletStatisticBuyPriceGt15kAllEntity


class TortoiseWalletTokenRepository(
    TortoiseGenericRepository,
    BaseWalletTokenRepository,
):
    model_class = WalletToken
    entity_class = WalletTokenEntity


class TortoiseWalletRepository(
    TortoiseGenericRepository,
    BaseWalletRepository,
):
    model_class = Wallet
    entity_class = WalletEntity

    # noinspection PyMethodMayBeStatic
    async def get_by_address(self, address: str) -> WalletEntity | None:
        return await Wallet.filter(address=address).first()

    # noinspection PyMethodMayBeStatic
    async def get_by_address_with_details_and_stats(self, address: str) -> WalletEntity | None:
        return (
            await Wallet.filter(address=address)
            .prefetch_related(
                "details",
                "stats_7d",
                "stats_30d",
                "stats_all",
            )
            .first()
        )

    async def get_wallets_for_update_stats(self, count: int = 1) -> list[WalletEntity]:
        query = queries.GET_WALLETS_FOR_UPDATE_STATS.format(count=count)
        res = await self._execute_query(query)
        return [WalletEntity(**obj) for obj in res[1] or []]

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
