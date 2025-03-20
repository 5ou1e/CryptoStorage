import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DECIMAL, UUID, BigInteger, Boolean, DateTime, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infra.db.models.sqlalchemy.common import Base, TimestampsMixin, UUIDIDMixin


class Swap(Base, UUIDIDMixin, TimestampsMixin):
    __tablename__ = "swap"

    wallet_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("wallet.id", ondelete="CASCADE"), sort_order=-999
    )
    token_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("token.id", ondelete="CASCADE"), sort_order=-999
    )
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    block_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    is_part_of_transaction_with_mt_3_swappers: Mapped[bool] = mapped_column(Boolean, default=False)
    is_part_of_arbitrage_swap_event: Mapped[bool] = mapped_column(Boolean, default=False)
    token_amount: Mapped[Decimal | None] = mapped_column(DECIMAL(40, 20), nullable=True)
    quote_amount: Mapped[Decimal | None] = mapped_column(DECIMAL(40, 20), nullable=True)
    price_usd: Mapped[Decimal | None] = mapped_column(DECIMAL(40, 20), nullable=True)
    event_type: Mapped[str | None] = mapped_column(String(15), nullable=True)
    tx_hash: Mapped[str | None] = mapped_column(String(90), nullable=True)

    wallet = relationship("Wallet", backref="swaps")
    token = relationship("Token", backref="swaps")

    __table_args__ = (
        Index("idx_swap_wallet_id", "wallet_id"),
        Index("idx_swap_token_id", "token_id"),
        # Index("idx_tx_hash", "tx_hash"),
        Index("idx_swap_block_id", "block_id"),
        Index("idx_swap_timestamp", "timestamp"),
    )
