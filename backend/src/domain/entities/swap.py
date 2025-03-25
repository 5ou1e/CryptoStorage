from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from uuid import UUID

from src.domain.entities.base_entity import BaseEntity, TimestampMixinEntity


class SwapEventType(StrEnum):
    BUY = "buy"
    SELL = "sell"


@dataclass(kw_only=False, slots=True)
class Swap(BaseEntity, TimestampMixinEntity):
    id: UUID
    wallet_id: UUID
    token_id: UUID
    tx_hash: str
    block_id: int
    timestamp: datetime | None = None
    event_type: SwapEventType | None = None
    quote_amount: Decimal | None = None
    token_amount: Decimal | None = None
    price_usd: Decimal | None = None
    is_part_of_transaction_with_mt_3_swappers: bool = False
    is_part_of_arbitrage_swap_event: bool = False
