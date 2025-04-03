from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from typing import List, Optional

from fastapi import Query
from pydantic import BaseModel, Field

from src.application.common.dto import PaginationResult, BaseSorting
from src.application.token.dto import TokenDTO
from src.domain.entities import SwapEventType


class GetWalletActivitiesSortingFields(StrEnum):
    BLOCK_ID_AT_ASC = "block_id"
    BLOCK_ID_DESC = "-block_id"
    CREATED_AT_ASC = "created_at"
    CREATED_AT_DESC = "-created_at"


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


class GetWalletActivitiesSorting(BaseSorting[GetWalletActivitiesSortingFields]):
    pass


class GetWalletActivitiesFilters(BaseModel):
    token__address: Optional[str] = Field(Query(None, description="Адрес токена"))
    event_type__in: Optional[List[SwapEventType]] = Field(
        Query(
            None,
            description="Тип свапа - покупка\продажа",
        )
    )
    block_id__gte: Optional[int] = Field(None, description="Дата создания >=")
    block_id__lte: Optional[int] = Field(None, description="Дата создания <=")
    created_at__gte: Optional[datetime] = Field(None, description="Дата создания >=")
    created_at__lte: Optional[datetime] = Field(None, description="Дата создания <=")
