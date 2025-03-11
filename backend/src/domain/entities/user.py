from dataclasses import dataclass
from datetime import datetime

from src.domain.entities.base_entity import (
    BaseEntity,
    TimestampMixinEntity,
)


@dataclass(kw_only=True)
class UserEntity(BaseEntity, TimestampMixinEntity):
    id: int | None = None
    username: str | None
    email: str = None
    hashed_password: str = None
    is_active: bool = True
    is_superuser: bool = False
    first_name: str | None = None
    last_name: str | None = None
    is_staff: bool = False
    date_joined: datetime = None

    @classmethod
    def create(
        cls,
        username: str,
        email: str,
        hashed_password: str,
    ) -> "UserEntity":
        user = cls(
            username=username,
            email=email,
            hashed_password=hashed_password,
        )
        return user
