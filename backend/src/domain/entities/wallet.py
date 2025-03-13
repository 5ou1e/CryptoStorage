from dataclasses import dataclass, field
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional
from uuid import UUID

from src.domain.entities.base_entity import BaseEntity, TimestampMixinEntity


@dataclass
class WalletEntity(
    BaseEntity,
    TimestampMixinEntity,
):
    id: Optional[UUID] = None
    address: Optional[str] = None
    last_stats_check: Optional[datetime] = None
    last_activity_timestamp: Optional[datetime] = None
    first_activity_timestamp: Optional[datetime] = None
    details: Optional["WalletDetailEntity"] = None
    stats_7d: Optional["WalletStatistic7dEntity"] = None
    stats_30d: Optional["WalletStatistic30dEntity"] = None
    stats_all: Optional["WalletStatisticAllEntity"] = None
    tokens: Optional[list["WalletTokenEntity"]] = field(default_factory=list)

    @property
    def is_need_update_stats_all(self) -> bool:
        """Неоходимо ли обновлять статистику за все время"""
        # Обновляем статистику за все время, только если есть неучтенная активность
        # Прибавляем 10 минут, чтобы исключить случай, когда появится новая активность в момент апдейта
        # Т.к временная метка апдейта устанавливается в конце процесса чека
        # В таком случае статистика посчитается еще 1 раз, но это не страшно
        if self.last_stats_check is None or self.last_activity_timestamp is None:
            return True
        return self.last_stats_check < self.last_activity_timestamp + timedelta(minutes=10)


@dataclass
class WalletDetailEntity(BaseEntity, TimestampMixinEntity):
    id: Optional[int] = None
    wallet_id: Optional[UUID] = None
    sol_balance: Optional[Decimal] = None
    is_scammer: bool = False
    is_bot: bool = False


@dataclass
class AbstractWalletStatisticEntity(BaseEntity, TimestampMixinEntity):
    id: Optional[int] = None
    wallet_id: Optional[UUID] = None
    winrate: Optional[Decimal] = None
    total_token_buy_amount_usd: Optional[Decimal] = None
    total_token_sell_amount_usd: Optional[Decimal] = None
    total_profit_usd: Optional[Decimal] = None
    total_profit_multiplier: Optional[float] = None
    total_token: Optional[int] = None
    total_token_buys: Optional[int] = None
    total_token_sales: Optional[int] = None
    token_with_buy_and_sell: Optional[int] = None
    token_with_buy: Optional[int] = None
    token_sell_without_buy: Optional[int] = None
    token_buy_without_sell: Optional[int] = None
    token_with_sell_amount_gt_buy_amount: Optional[int] = None
    token_avg_buy_amount: Optional[Decimal] = None
    token_median_buy_amount: Optional[Decimal] = None
    token_first_buy_avg_price_usd: Optional[Decimal] = None
    token_first_buy_median_price_usd: Optional[Decimal] = None
    token_avg_profit_usd: Optional[Decimal] = None
    token_buy_sell_duration_avg: Optional[int] = None
    token_buy_sell_duration_median: Optional[int] = None
    first_transaction_timestamp: Optional[int] = None
    pnl_lt_minus_dot5_num: Optional[int] = None
    pnl_minus_dot5_0x_num: Optional[int] = None
    pnl_lt_2x_num: Optional[int] = None
    pnl_2x_5x_num: Optional[int] = None
    pnl_gt_5x_num: Optional[int] = None
    pnl_lt_minus_dot5_percent: Optional[float] = None
    pnl_minus_dot5_0x_percent: Optional[float] = None
    pnl_lt_2x_percent: Optional[float] = None
    pnl_2x_5x_percent: Optional[float] = None
    pnl_gt_5x_percent: Optional[float] = None
    total_swaps_from_arbitrage_swap_events: Optional[int] = 0
    total_swaps_from_txs_with_mt_3_swappers: Optional[int] = 0

    @property
    def total_buys_and_sales_count(self) -> int:
        return (self.total_token_buys or 0) + (self.total_token_sales or 0)


@dataclass
class WalletStatistic7dEntity(AbstractWalletStatisticEntity):
    pass


@dataclass
class WalletStatistic30dEntity(AbstractWalletStatisticEntity):
    pass


@dataclass
class WalletStatisticAllEntity(AbstractWalletStatisticEntity):
    pass


@dataclass
class WalletStatisticBuyPriceGt15k7dEntity(AbstractWalletStatisticEntity):
    pass


@dataclass
class WalletStatisticBuyPriceGt15k30dEntity(AbstractWalletStatisticEntity):
    pass


@dataclass
class WalletStatisticBuyPriceGt15kAllEntity(AbstractWalletStatisticEntity):
    pass


@dataclass
class WalletTokenEntity(BaseEntity, TimestampMixinEntity):
    id: Optional[UUID] = None
    wallet_id: Optional[UUID] = None
    token_id: Optional[UUID] = None
    total_buys_count: int = 0
    total_buy_amount_usd: Decimal = Decimal(0)
    total_buy_amount_token: Decimal = Decimal(0)
    first_buy_price_usd: Optional[Decimal] = None
    first_buy_timestamp: Optional[int] = None
    total_sales_count: int = 0
    total_sell_amount_usd: Decimal = Decimal(0)
    total_sell_amount_token: Decimal = Decimal(0)
    first_sell_price_usd: Optional[Decimal] = None
    first_sell_timestamp: Optional[int] = None
    last_activity_timestamp: Optional[int] = None
    total_profit_usd: Decimal = Decimal(0)
    total_profit_percent: Optional[float] = None
    first_buy_sell_duration: Optional[int] = None
    total_swaps_from_txs_with_mt_3_swappers: int = 0
    total_swaps_from_arbitrage_swap_events: int = 0


@dataclass
class TgSentWalletEntity(BaseEntity, TimestampMixinEntity):
    id: Optional[int] = None
    wallet_id: Optional[UUID] = None
