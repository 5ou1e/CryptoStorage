import logging
from typing import Optional
from uuid import UUID

from sqlalchemy import and_, select, text
from sqlalchemy.orm import selectinload
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
from src.domain.entities.wallet import (
    WalletStatisticBuyPriceGt15k7d as WalletStatisticBuyPriceGt15k7dEntity,
)
from src.domain.entities.wallet import (
    WalletStatisticBuyPriceGt15k30d as WalletStatisticBuyPriceGt15k30dEntity,
)
from src.domain.entities.wallet import (
    WalletStatisticBuyPriceGt15kAll as WalletStatisticBuyPriceGt15kAllEntity,
)
from src.domain.entities.wallet import WalletToken as WalletTokenEntity
from src.infra.db import queries
from src.infra.db.sqlalchemy.models import (
    Wallet,
    WalletStatistic7d,
    WalletStatistic30d,
    WalletStatisticAll,
    WalletStatisticBuyPriceGt15k7d,
    WalletStatisticBuyPriceGt15k30d,
    WalletStatisticBuyPriceGt15kAll,
    WalletToken,
)

from .common.queries import get_bulk_update_or_create_wallet_token_with_merge_stmt
from .generic_repository import SQLAlchemyGenericRepository

logger = logging.getLogger(__name__)


class SQLAlchemyWalletStatistic7dRepository(
    SQLAlchemyGenericRepository,
    WalletStatistic7dRepositoryInterface,
):
    model_class = WalletStatistic7d
    entity_class = WalletStatistic7dEntity


class SQLAlchemyWalletStatistic30dRepository(
    SQLAlchemyGenericRepository,
    WalletStatistic30dRepositoryInterface,
):
    model_class = WalletStatistic30d
    entity_class = WalletStatistic30dEntity


class SQLAlchemyWalletStatisticAllRepository(
    SQLAlchemyGenericRepository,
    WalletStatisticAllRepositoryInterface,
):
    model_class = WalletStatisticAll
    entity_class = WalletStatisticAllEntity


class SQLAlchemyWalletStatisticBuyPriceGt15k7dRepository(
    SQLAlchemyGenericRepository,
    WalletStatisticBuyPriceGt15k7dRepositoryInterface,
):
    model_class = WalletStatisticBuyPriceGt15k7d
    entity_class = WalletStatisticBuyPriceGt15k7dEntity


class SQLAlchemyWalletStatisticBuyPriceGt15k30dRepository(
    SQLAlchemyGenericRepository,
    WalletStatisticBuyPriceGt15k30dRepositoryInterface,
):
    model_class = WalletStatisticBuyPriceGt15k30d
    entity_class = WalletStatisticBuyPriceGt15k30dEntity


class SQLAlchemyWalletStatisticBuyPriceGt15kAllRepository(
    SQLAlchemyGenericRepository,
    WalletStatisticBuyPriceGt15kAllRepositoryInterface,
):
    model_class = WalletStatisticBuyPriceGt15kAll
    entity_class = WalletStatisticBuyPriceGt15kAllEntity


class SQLAlchemyWalletTokenRepository(
    SQLAlchemyGenericRepository,
    WalletTokenRepositoryInterface,
):
    model_class = WalletToken
    entity_class = WalletTokenEntity

    async def get_wallet_tokens_by_wallets_list(self, wallet_ids: list[UUID]):
        query = select(*self.model_class.__table__.columns).where(
            self.model_class.wallet_id.in_([id_ for id_ in wallet_ids])
        )

        connection = await self._session.connection()
        result = await connection.execute(query)
        return [self.entity_class(**row) for row in result.mappings().all()]

    async def get_wallet_tokens_by_wallet_for_buygt15k_statistic(
        self, wallet_id: UUID
    ) -> list[WalletTokenEntity]:
        query = select(*self.model_class.__table__.columns).where(
            WalletToken.wallet_id == wallet_id,
            self.model_class.first_buy_price_usd >= 0.000008,
            self.model_class.total_buy_amount_usd >= 100,
        )
        connection = await self._session.connection()
        result = await connection.execute(query)
        return [self.entity_class(**row) for row in result.mappings().all()]

    async def bulk_update_or_create_wallet_token_with_merge(
        self,
        objects: list[WalletTokenEntity],
        batch_size: Optional[int] = None,
    ) -> list[WalletTokenEntity]:
        """Массовая вставка записей с обновлением и слиянием при конфликте"""
        if not objects:
            return []
        values = [obj.to_dict() for obj in objects]
        stmt = get_bulk_update_or_create_wallet_token_with_merge_stmt()

        connection = await self._session.connection()

        if batch_size:
            [
                await connection.execute(stmt, values[i : i + batch_size])
                for i in range(0, len(objects), batch_size)
            ]
        else:
            await connection.execute(stmt, values)
        return objects


class SQLAlchemyWalletRepository(
    SQLAlchemyGenericRepository,
    WalletRepositoryInterface,
):
    model_class = Wallet
    entity_class = WalletEntity

    async def get_by_address(self, address: str) -> WalletEntity | None:
        stmt = select(self.model_class).where(self.model_class.address == address)
        result = await self._session.execute(stmt)
        return result.scalars().first()

    async def get_wallets_for_update_stats(self, count: int = 1) -> list[WalletEntity]:
        _query = queries.GET_WALLETS_FOR_UPDATE_STATS.format(count=count)
        query = text(_query)
        connection = await self._session.connection()
        result = await connection.execute(query)
        return [self.entity_class(**row) for row in result.mappings().all()]

    async def get_wallets_for_buygt15k_statistic(self) -> list[WalletEntity]:
        """Возвращает подходящие кошельки для подсчета статистики buygt15k"""
        query = (
            select(*self.model_class.__table__.columns)
            .join(WalletStatisticAll, WalletStatisticAll.wallet_id == Wallet.id)
            .join(WalletStatistic7d, WalletStatistic7d.wallet_id == Wallet.id)
            .where(
                and_(
                    WalletStatisticAll.winrate >= 30,
                    WalletStatisticAll.total_profit_usd >= 2000,
                    WalletStatisticAll.total_profit_multiplier >= 30,
                    WalletStatisticAll.token_avg_buy_amount.between(150, 1000),
                    WalletStatisticAll.token_buy_sell_duration_median >= 60,
                    WalletStatistic7d.total_token >= 4,
                    self.model_class.is_scammer == False,
                    self.model_class.is_bot == False,
                )
            )
        )
        connection = await self._session.connection()
        result = await connection.execute(query)
        return [self.entity_class(**row) for row in result.mappings().all()]

    async def get_wallets_for_copytraders_statistic(self) -> list[WalletEntity]:
        """Возвращает подходящие кошельки для подсчета статистики copytraders"""
        query = (
            select(*self.model_class.__table__.columns)
            .join(WalletStatistic30d, WalletStatistic30d.wallet_id == Wallet.id)
            .where(
                and_(
                    WalletStatistic30d.total_profit_usd >= 15000,
                    WalletStatistic30d.total_token >= 100,
                    WalletStatistic30d.token_buy_sell_duration_median >= 60,
                    self.model_class.is_scammer == False,
                    self.model_class.is_bot == False,
                )
            )
        )
        connection = await self._session.connection()
        result = await connection.execute(query)
        return [self.entity_class(**row) for row in result.mappings().all()]

    # noinspection PyMethodMayBeStatic
    async def get_wallets_by_token_addresses(
        self,
        token_addresses: list[str],
        matching_tokens_percent: int = 100,  # Мин. процент совпадающих токенов
        filter_by: Optional[dict] = None,
        prefetch: Optional[list] = None,
    ) -> list[WalletEntity]:
        # Получает кошельки, которые взаимодействовали со всеми переданными адресами токенов
        raise NotImplementedError
