from dataclasses import dataclass, field
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional
from uuid import UUID

import pytz

from src.domain.entities.base_entity import BaseEntity, TimestampMixinEntity


@dataclass(kw_only=True, slots=True)
class Wallet(
    BaseEntity,
    TimestampMixinEntity,
):
    id: Optional[UUID] = None
    address: Optional[str] = None
    last_stats_check: Optional[datetime] = None
    last_activity_timestamp: Optional[datetime] = None
    first_activity_timestamp: Optional[datetime] = None
    sol_balance: Optional[Decimal] = None
    is_scammer: bool = False
    is_bot: bool = False
    stats_7d: Optional["WalletStatistic7d"] = None
    stats_30d: Optional["WalletStatistic30d"] = None
    stats_all: Optional["WalletStatisticAll"] = None  # field(default=None, repr=False)
    tokens: list["WalletToken"] = field(default_factory=list)


@dataclass(slots=True)
class AbstractWalletStatistic(BaseEntity, TimestampMixinEntity):
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
class WalletStatistic7d(AbstractWalletStatistic):
    pass


@dataclass
class WalletStatistic30d(AbstractWalletStatistic):
    pass


@dataclass
class WalletStatisticAll(AbstractWalletStatistic):
    pass


@dataclass
class WalletStatisticBuyPriceGt15k7d(AbstractWalletStatistic):
    pass


@dataclass
class WalletStatisticBuyPriceGt15k30d(AbstractWalletStatistic):
    pass


@dataclass
class WalletStatisticBuyPriceGt15kAll(AbstractWalletStatistic):
    pass


@dataclass(slots=True)
class WalletToken(BaseEntity, TimestampMixinEntity):
    id: Optional[UUID] = None
    wallet_id: Optional[UUID] = None
    token_id: Optional[UUID] = None
    total_buys_count: int = 0
    total_buy_amount_usd: Decimal = Decimal(0)
    total_buy_amount_token: Decimal = Decimal(0)
    first_buy_price_usd: Optional[Decimal] = None
    first_buy_timestamp: Optional[datetime] = None
    total_sales_count: int = 0
    total_sell_amount_usd: Decimal = Decimal(0)
    total_sell_amount_token: Decimal = Decimal(0)
    first_sell_price_usd: Optional[Decimal] = None
    first_sell_timestamp: Optional[datetime] = None
    last_activity_timestamp: Optional[datetime] = None
    total_profit_usd: Decimal = Decimal(0)
    total_profit_percent: Optional[float] = None
    first_buy_sell_duration: Optional[int] = None
    total_swaps_from_txs_with_mt_3_swappers: int = 0
    total_swaps_from_arbitrage_swap_events: int = 0


@dataclass
class TgSentWallet(BaseEntity, TimestampMixinEntity):
    wallet_id: Optional[UUID] = None
