from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from src.domain.entities.base_entity import BaseEntity, TimestampMixinEntity


@dataclass(kw_only=True)
class TokenEntity(BaseEntity, TimestampMixinEntity):
    id: UUID = None
    address: str = None
    name: str | None = None
    symbol: str | None = None
    uri: str | None = None
    logo: str | None = None
    created_on: str | None = None
    is_metadata_parsed: bool = None


@dataclass
class TokenPriceEntity(BaseEntity, TimestampMixinEntity):
    id: int
    token_id: UUID
    price_usd: Decimal | None
    minute: datetime
