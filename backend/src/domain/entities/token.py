from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from src.domain.entities.base_entity import BaseEntity, TimestampMixinEntity


@dataclass(kw_only=True, slots=True)
class Token(BaseEntity, TimestampMixinEntity):
    id: UUID
    address: str
    name: str | None = None
    symbol: str | None = None
    uri: str | None = None
    logo: str | None = None
    created_on: str | None = None
    is_metadata_parsed: bool = False


@dataclass
class TokenPrice(BaseEntity, TimestampMixinEntity):
    id: UUID
    token_id: UUID
    price_usd: Decimal
    minute: datetime
