from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from fastapi import Query
from pydantic import BaseModel, Field

from src.application.common.dto import PaginationResult
from src.application.token.dto import TokenDTO


class WalletActivityDTO(BaseModel):
    token: TokenDTO
    tx_hash: str
    timestamp: datetime
    event_type: str
    quote_amount: Decimal
    token_amount: Decimal
    price_usd: Decimal
    is_part_of_transaction_with_mt_3_swappers: bool
    is_part_of_arbitrage_swap_event: bool

    class Config:
        from_attributes = True


class WalletActivitiesDTO(BaseModel):
    activities: List[WalletActivityDTO]


class WalletActivitiesPageDTO(WalletActivitiesDTO):
    pagination: PaginationResult


class GetWalletActivitiesFilters(BaseModel):
    token__address: Optional[str] = Field(Query(None, description="Адрес токена"))
    event_type__in: Optional[List[str]] = Field(
        Query(
            None,
            description="Тип свапа - покупка\продажа",
        )
    )
    created_at__gte: Optional[datetime] = Field(None, description="Дата создания >=")
    created_at__lte: Optional[datetime] = Field(None, description="Дата создания <=")
