from typing import List, Optional

from fastapi import Query
from pydantic import BaseModel, Field
from src.application.common.dto import PaginationResult

from .wallet_stats import WalletStats7dDTO, WalletStats30dDTO, WalletStatsAllDTO


class WalletDTO(BaseModel):
    address: str
    is_bot: Optional[bool] = None
    is_scammer: Optional[bool] = None
    stats_7d: Optional[WalletStats7dDTO] = None
    stats_30d: Optional[WalletStats30dDTO] = None
    stats_all: Optional[WalletStatsAllDTO] = None

    class Config:
        from_attributes = True


class WalletsDTO(BaseModel):
    wallets: List[WalletDTO]


class WalletsPageDTO(WalletsDTO):
    pagination: PaginationResult


class GetWalletsFilters(BaseModel):
    is_bot: Optional[bool] = Field(
        Query(
            None,
            description="Является ли кошелек арбитраж-ботом",
        )
    )
    is_scammer: Optional[bool] = Field(
        Query(
            None,
            description="Является ли кошелек скамерским",
        )
    )
    stats_all__winrate__gte: Optional[float] = Field(
        Query(
            None,
            description="(All) Винрейт в % больше",
        )
    )
    stats_all__winrate__lte: Optional[float] = Field(
        Query(
            None,
            description="(All) Винрейт в % меньше",
        )
    )

    # is_bot__in: Optional[List[bool]] = Field(Query(None), description="")
    # stats_all__total_profit_usd__gte: Optional[float] = Field(None, description="")
    # stats_all__total_profit_usd__lte: Optional[float] = Field(None, description="")
    # stats_all__total_profit_multiplier__gte: Optional[float] = Field(None, description="")
    # stats_all__total_profit_multiplier__lte: Optional[float] = Field(None, description="")
    stats_all__total_token__gte: Optional[int] = Field(
        Query(
            None,
            description="(All) Всего токенов",
        )
    )
    # stats_all__total_token__lte: Optional[int] = Field(None, description="")
    # stats_all__token_avg_buy_amount__gte: Optional[float] = Field(None, description="")
    # stats_all__token_avg_buy_amount__lte: Optional[float] = Field(None, description="")
    # stats_all__token_avg_profit_usd__gte: Optional[float] = Field(None, description="")
    # stats_all__token_avg_profit_usd__lte: Optional[float] = Field(None, description="")
    # stats_all__pnl_gt_5x_percent__gte: Optional[float] = Field(None, description="")
    # stats_all__pnl_gt_5x_percent__lte: Optional[float] = Field(None, description="")
    # stats_all__token_first_buy_median_price_usd__gte: Optional[float] = Field(None, description="")
    # stats_all__token_first_buy_median_price_usd__lte: Optional[float] = Field(None, description="")
    # stats_all__token_buy_sell_duration_median__gte: Optional[float] = Field(None, description="")
    # stats_all__token_buy_sell_duration_median__lte: Optional[float] = Field(None, description="")
    # stats_7d__winrate__gte: Optional[float] = Field(None, description="")
    # stats_7d__winrate__lte: Optional[float] = Field(None, description="")
    # stats_7d__total_profit_usd__gte: Optional[float] = Field(None, description="")
    # stats_7d__total_profit_usd__lte: Optional[float] = Field(None, description="")
    # stats_7d__total_profit_multiplier__gte: Optional[float] = Field(None, description="")
    # stats_7d__total_profit_multiplier__lte: Optional[float] = Field(None, description="")
    # stats_7d__total_token__gte: Optional[int] = Field(None, description="")
    # stats_7d__total_token__lte: Optional[int] = Field(None, description="")
    # stats_7d__token_avg_buy_amount__gte: Optional[float] = Field(None, description="")
    # stats_7d__token_avg_buy_amount__lte: Optional[float] = Field(None, description="")
    # stats_7d__token_avg_profit_usd__gte: Optional[float] = Field(None, description="")
    # stats_7d__token_avg_profit_usd__lte: Optional[float] = Field(None, description="")
    # stats_7d__pnl_gt_5x_percent__gte: Optional[float] = Field(None, description="")
    # stats_7d__pnl_gt_5x_percent__lte: Optional[float] = Field(None, description="")
    # stats_7d__token_first_buy_median_price_usd__gte: Optional[float] = Field(None, description="")
    # stats_7d__token_first_buy_median_price_usd__lte: Optional[float] = Field(None, description="")
    # stats_7d__token_buy_sell_duration_median__gte: Optional[float] = Field(None, description="")
    # stats_7d__token_buy_sell_duration_median__lte: Optional[float] = Field(None, description="")
    # stats_30d__winrate__gte: Optional[float] = Field(None, description="")
    # stats_30d__winrate__lte: Optional[float] = Field(None, description="")
    # stats_30d__total_profit_usd__gte: Optional[float] = Field(None, description="")
    # stats_30d__total_profit_usd__lte: Optional[float] = Field(None, description="")
    # stats_30d__total_profit_multiplier__gte: Optional[float] = Field(None, description="")
    # stats_30d__total_profit_multiplier__lte: Optional[float] = Field(None, description="")
    # stats_30d__total_token__gte: Optional[int] = Field(None, description="")
    # stats_30d__total_token__lte: Optional[int] = Field(None, description="")
    # stats_30d__token_avg_buy_amount__gte: Optional[float] = Field(None, description="")
    # stats_30d__token_avg_buy_amount__lte: Optional[float] = Field(None, description="")
    # stats_30d__token_avg_profit_usd__gte: Optional[float] = Field(None, description="")
    # stats_30d__token_avg_profit_usd__lte: Optional[float] = Field(None, description="")
    # stats_30d__pnl_gt_5x_percent__gte: Optional[float] = Field(None, description="")
    # stats_30d__pnl_gt_5x_percent__lte: Optional[float] = Field(None, description="")
    # stats_30d__token_first_buy_median_price_usd__gte: Optional[float] = Field(None, description="")
    # stats_30d__token_first_buy_median_price_usd__lte: Optional[float] = Field(None, description="")
    # stats_30d__token_buy_sell_duration_median__gte: Optional[float] = Field(None, description="")
    # stats_30d__token_buy_sell_duration_median__lte: Optional[float] = Field(None, description="")
