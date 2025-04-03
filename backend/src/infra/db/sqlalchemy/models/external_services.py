from datetime import datetime

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from src.infra.db.sqlalchemy.models.common import Base, UUIDIDMixin


class FlipsideConfig(Base, UUIDIDMixin):
    __tablename__ = "flipsidecrypto_config"

    swaps_parsed_until_block_timestamp: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = {"comment": "Конфиг FlipsideCrypto"}


class FlipsideAccount(Base, UUIDIDMixin):
    __tablename__ = "flipsidecrypto_account"

    api_key: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    __table_args__ = {"comment": "Аккаунты FlipsideCrypto"}
