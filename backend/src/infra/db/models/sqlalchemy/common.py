import uuid
from datetime import datetime

from sqlalchemy import UUID, DateTime, Integer, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


# declarative base class
class Base(DeclarativeBase):
    pass


class IntIDMixin:
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )


class UUIDIDMixin:
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid1,
    )


class TimestampsMixin:
    """Базовый класс для моделей с временными метками"""

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )
