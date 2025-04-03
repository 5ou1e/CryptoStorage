from enum import StrEnum
from typing import List, Optional

from fastapi import Query
from pydantic import BaseModel, Field, create_model

from src.application.common.dto import PaginationResult, BaseSorting

from .wallet_stats import WalletStats7dDTO, WalletStats30dDTO, WalletStatsAllDTO


class GetWalletsSortingFields(StrEnum):
    CREATED_AT_ASC = "created_at"
    CREATED_AT_DESC = "-created_at"


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


class GetWalletsSorting(BaseSorting[GetWalletsSortingFields]):
    pass


class GetWalletsFiltersBase(BaseModel):
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


def generate_wallet_stats_filter_fields(prefix: str):
    return {
        f"{prefix}__winrate__gte": (Optional[int], Field(Query(None, description=f""))),
        f"{prefix}__winrate__lte": (Optional[int], Field(Query(None, description=f""))),
        f"{prefix}__total_profit_usd__gte": (Optional[int], Field(Query(None, description=f""))),
        f"{prefix}__total_profit_usd__lte": (Optional[int], Field(Query(None, description=f""))),
        f"{prefix}__total_profit_multiplier__gte": (Optional[int], Field(Query(None, description=f""))),
        f"{prefix}__total_profit_multiplier__lte": (Optional[int], Field(Query(None, description=f""))),
        f"{prefix}__total_token__gte": (
            Optional[int],
            Field(Query(None, description=f"({prefix.upper()}) Всего токенов ≥")),
        ),
        f"{prefix}__total_token__lte": (
            Optional[int],
            Field(Query(None, description=f"({prefix.upper()}) Всего токенов ≤")),
        ),
        f"{prefix}__token_avg_buy_amount__gte": (
            Optional[float],
            Field(Query(None, description=f"({prefix.upper()}) Средний объем покупки ≥")),
        ),
        f"{prefix}__token_avg_buy_amount__lte": (
            Optional[float],
            Field(Query(None, description=f"({prefix.upper()}) Средний объем покупки ≤")),
        ),
        f"{prefix}__token_avg_profit_usd__gte": (
            Optional[float],
            Field(Query(None, description=f"({prefix.upper()}) Средний профит (USD) ≥")),
        ),
        f"{prefix}__token_avg_profit_usd__lte": (
            Optional[float],
            Field(Query(None, description=f"({prefix.upper()}) Средний профит (USD) ≤")),
        ),
        f"{prefix}__pnl_gt_5x_percent__gte": (Optional[float], Field(Query(None, description=f""))),
        f"{prefix}__pnl_gt_5x_percent__lte": (Optional[float], Field(Query(None, description=f""))),
        f"{prefix}__token_first_buy_median_price_usd__gte": (Optional[float], Field(Query(None, description=f""))),
        f"{prefix}__token_first_buy_median_price_usd__lte": (Optional[float], Field(Query(None, description=f""))),
        f"{prefix}__token_buy_sell_duration_median__gte": (Optional[float], Field(Query(None, description=f""))),
        f"{prefix}__token_buy_sell_duration_median__lte": (Optional[float], Field(Query(None, description=f""))),
    }


GetWalletsFilters = create_model(
    "GetWalletsFilters",
    # **generate_wallet_stats_filter_fields("stats_all"),
    # **generate_wallet_stats_filter_fields("stats_7d"),
    # **generate_wallet_stats_filter_fields("stats_30d"),
    __base__=GetWalletsFiltersBase,
)
