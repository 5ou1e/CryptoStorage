import logging
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import selectinload

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
from src.infra.db.models.sqlalchemy import (
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
    SQLAlchemyGenericRepository,
)

logger = logging.getLogger(__name__)


class SQLAlchemyWalletDetailRepository(
    SQLAlchemyGenericRepository,
    BaseWalletDetailRepository,
):
    model_class = WalletDetail
    entity_class = WalletDetailEntity


class SQLAlchemyWalletStatistic7dRepository(
    SQLAlchemyGenericRepository,
    BaseWalletStatistic7dRepository,
):
    model_class = WalletStatistic7d
    entity_class = WalletStatistic7dEntity


class SQLAlchemyWalletStatistic30dRepository(
    SQLAlchemyGenericRepository,
    BaseWalletStatistic30dRepository,
):
    model_class = WalletStatistic30d
    entity_class = WalletStatistic30dEntity


class SQLAlchemyWalletStatisticAllRepository(
    SQLAlchemyGenericRepository,
    BaseWalletStatisticAllRepository,
):
    model_class = WalletStatisticAll
    entity_class = WalletStatisticAllEntity


class SQLAlchemyWalletStatisticBuyPriceGt15k7dRepository(
    SQLAlchemyGenericRepository,
    BaseWalletStatisticBuyPriceGt15k7dRepository,
):
    model_class = WalletStatisticBuyPriceGt15k7d
    entity_class = WalletStatisticBuyPriceGt15k7dEntity


class SQLAlchemyWalletStatisticBuyPriceGt15k30dRepository(
    SQLAlchemyGenericRepository,
    BaseWalletStatisticBuyPriceGt15k30dRepository,
):
    model_class = WalletStatisticBuyPriceGt15k30d
    entity_class = WalletStatisticBuyPriceGt15k30dEntity


class SQLAlchemyWalletStatisticBuyPriceGt15kAllRepository(
    SQLAlchemyGenericRepository,
    BaseWalletStatisticBuyPriceGt15kAllRepository,
):
    model_class = WalletStatisticBuyPriceGt15kAll
    entity_class = WalletStatisticBuyPriceGt15kAllEntity


class SQLAlchemyWalletTokenRepository(
    SQLAlchemyGenericRepository,
    BaseWalletTokenRepository,
):
    model_class = WalletToken
    entity_class = WalletTokenEntity


class SQLAlchemyWalletRepository(
    SQLAlchemyGenericRepository,
    BaseWalletRepository,
):
    model_class = Wallet
    entity_class = WalletEntity

    async def get_by_address(self, address: str) -> WalletEntity | None:
        stmt = select(self.model_class).where(self.model_class.address == address)
        result = await self._session.execute(stmt)
        return result.scalars().first()

    async def get_by_address_with_details_and_stats(self, address: str) -> WalletEntity | None:
        stmt = (
            select(Wallet)
            .where(Wallet.address == address)
            .options(
                selectinload(Wallet.details),
                selectinload(Wallet.stats_7d),
                selectinload(Wallet.stats_30d),
                selectinload(Wallet.stats_all),
            )
        )
        result = await self._session.execute(stmt)
        return result.scalars().first()

    async def get_wallets_for_update_stats(self, count: int = 1) -> list[WalletEntity]:
        raise NotImplementedError

    # noinspection PyMethodMayBeStatic
    async def get_wallets_by_token_addresses(
        self,
        token_addresses: list[str],
        matching_tokens_percent: int = 100,  # Мин. процент совпадающих токенов
        filter_by: Optional[dict] = None,
        prefetch: Optional[list] = None,
    ):
        # Получает кошельки, которые взаимодействовали со всеми переданными адресами токенов
        raise NotImplementedError
