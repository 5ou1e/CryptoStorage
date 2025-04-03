from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

import pytz

from src.domain.entities.base_entity import BaseEntity, TimestampMixinEntity


@dataclass(kw_only=True)
class User(BaseEntity, TimestampMixinEntity):
    id: UUID | None = None  # Generates in DB
    username: str
    email: str
    hashed_password: str
    first_name: str | None = None
    last_name: str | None = None
    is_active: bool = True
    is_superuser: bool = False
    is_staff: bool = False
    date_joined: datetime | None = None
    last_login: datetime | None = None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def create(
        cls,
        username: str,
        email: str,
        hashed_password: str,
    ) -> "User":
        now = datetime.now(pytz.UTC)
        user = cls(
            username=username,
            email=email,
            hashed_password=hashed_password,
            created_at=now,
            updated_at=now,
        )
        return user
