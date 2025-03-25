from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from src.domain.entities.base_entity import BaseEntity, TimestampMixinEntity


@dataclass(kw_only=True, slots=True)
class FlipsideAccount(BaseEntity, TimestampMixinEntity):
    id: UUID
    api_key: str
    is_active: bool


@dataclass(kw_only=True, slots=True)
class FlipsideConfig(BaseEntity, TimestampMixinEntity):
    id: UUID
    swaps_parsed_until_block_timestamp: datetime
