from datetime import datetime

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, IntIDMixin, TimestampsMixin


class User(Base, IntIDMixin, TimestampsMixin):
    __tablename__ = "auth_user"

    username: Mapped[str | None] = mapped_column(String(50), unique=True, nullable=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    first_name: Mapped[str | None] = mapped_column(String(150), nullable=True, default="")
    last_name: Mapped[str | None] = mapped_column(String(150), nullable=True, default="")
    is_staff: Mapped[bool] = mapped_column(Boolean, default=False)
    date_joined: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
    )

    class PydanticMeta:
        exclude = ["hashed_password"]
