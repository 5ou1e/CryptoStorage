from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    DECIMAL,
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .common import Base, TimestampsMixin, UUIDIDMixin


class Token(Base, UUIDIDMixin, TimestampsMixin):
    __tablename__ = "token"

    is_metadata_parsed: Mapped[bool] = mapped_column(Boolean, default=False)
    address: Mapped[str] = mapped_column(String(90), unique=True, nullable=False)
    name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    symbol: Mapped[str | None] = mapped_column(String(100), nullable=True)
    uri: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Token Metaplex Metadata Uri",
    )
    logo: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_on: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        comment="Создан на",
    )

    __table_args__ = (Index("idx_token_is_metadata_parsed", "is_metadata_parsed"),)

    def __str__(self):
        return self.address


class TokenPrice(Base, UUIDIDMixin, TimestampsMixin):
    __tablename__ = "token_price"

    token_id: Mapped["Token.id.type"] = mapped_column(ForeignKey("token.id"), nullable=False, sort_order=-999)
    minute: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    price_usd: Mapped[Decimal | None] = mapped_column(DECIMAL(40, 20), nullable=True)

    token: Mapped["Token"] = relationship("Token", backref="token_price")

    __table_args__ = (
        UniqueConstraint(
            "token_id",
            "minute",
            name="_token_minute_uc",
        ),
    )

    def __str__(self):
        return f"Цена {self.token.symbol} в {self.minute}"
