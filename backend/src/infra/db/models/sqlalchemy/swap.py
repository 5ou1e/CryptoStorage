import uuid
from decimal import Decimal

from sqlalchemy import (
    DECIMAL,
    UUID,
    BigInteger,
    Boolean,
    ForeignKey,
    Index,
    String,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from src.infra.db.models.sqlalchemy.base import (
    Base,
    TimestampsMixin,
    UUIDIDMixin,
)


class Swap(Base, UUIDIDMixin, TimestampsMixin):
    __tablename__ = "swap"

    tx_hash: Mapped[str | None] = mapped_column(String(90), nullable=True)
    block_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    timestamp: Mapped[int | None] = mapped_column(BigInteger, nullable=True)

    event_type: Mapped[str | None] = mapped_column(String(15), nullable=True)

    quote_amount: Mapped[Decimal | None] = mapped_column(DECIMAL(40, 20), nullable=True)
    token_amount: Mapped[Decimal | None] = mapped_column(DECIMAL(40, 20), nullable=True)
    cost_usd: Mapped[Decimal | None] = mapped_column(DECIMAL(40, 20), nullable=True)
    price_usd: Mapped[Decimal | None] = mapped_column(DECIMAL(40, 20), nullable=True)

    is_part_of_transaction_with_mt_3_swappers: Mapped[bool] = mapped_column(Boolean, default=False)
    is_part_of_arbitrage_swap_event: Mapped[bool] = mapped_column(Boolean, default=False)

    wallet_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("wallet.id", ondelete="CASCADE"),
        index=True,
    )
    token_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("token.id", ondelete="CASCADE"),
        index=True,
    )

    wallet = relationship("Wallet", backref="swaps")
    token = relationship("Token", backref="swaps")

    __table_args__ = (
        Index("idx_tx_hash", "tx_hash"),
        Index("idx_block_id", "block_id"),
        Index("idx_timestamp", "timestamp"),
    )
