from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from src.domain.entities.base_entity import (
    BaseEntity,
    TimestampMixinEntity,
)


@dataclass
class SwapEntity(BaseEntity, TimestampMixinEntity):
    id: UUID
    wallet_id: UUID
    token_id: UUID
    tx_hash: str | None
    block_id: int | None
    timestamp: int | None
    event_type: str | None
    quote_amount: Decimal | None
    token_amount: Decimal | None
    cost_usd: Decimal | None
    price_usd: Decimal | None
    is_part_of_transaction_with_mt_3_swappers: bool
    is_part_of_arbitrage_swap_event: bool
