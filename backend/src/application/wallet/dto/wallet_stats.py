from decimal import Decimal
from typing import Optional

from pydantic import BaseModel


class BaseWalletStatsDTO(BaseModel):
    winrate: Optional[Decimal] = None
    total_token_buy_amount_usd: Optional[Decimal] = None
    total_token_sell_amount_usd: Optional[Decimal] = None
    total_profit_usd: Optional[Decimal] = None
    total_profit_multiplier: Optional[float] = None
    total_token: Optional[int] = 123
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

    class Config:
        from_attributes = True


class WalletStats7dDTO(BaseWalletStatsDTO):
    pass


class WalletStats30dDTO(BaseWalletStatsDTO):
    pass


class WalletStatsAllDTO(BaseWalletStatsDTO):
    pass
