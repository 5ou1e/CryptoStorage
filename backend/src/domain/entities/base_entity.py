from abc import ABC
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from mashumaro import DataClassDictMixin
from mashumaro.types import SerializationStrategy


class TsSerializationStrategy(SerializationStrategy, use_annotations=False):
    def serialize(self, value: datetime) -> datetime:
        """Для сериализации datetime -> datetime а не в str"""
        return value


@dataclass
class BaseEntity(DataClassDictMixin, ABC):
    """Базовый класс Entity"""

    class Config:
        serialization_strategy = {
            datetime: TsSerializationStrategy(),
        }


@dataclass(kw_only=True)
class TimestampMixinEntity:
    """Миксин с timestamp-полями"""

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
