import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    DECIMAL,
    UUID,
    BigInteger,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Identity,
    Index,
    Integer,
    PrimaryKeyConstraint,
    Sequence,
    String,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infra.db.sqlalchemy.models.common import Base, IntIDMixin, TimestampsMixin, UUIDIDMixin


class WalletFKPKMixin:
    """Миксин для FK/PK на таблицу wallet"""

    wallet_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("wallet.id", ondelete="CASCADE"), primary_key=True, sort_order=-999
    )


class Wallet(Base, UUIDIDMixin, TimestampsMixin):
    wallet = None
    __tablename__ = "wallet"

    last_stats_check: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_activity_timestamp: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    first_activity_timestamp: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    is_scammer: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    is_bot: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    sol_balance: Mapped[Decimal] = mapped_column(DECIMAL(50, 20), nullable=True)

    address: Mapped[str] = mapped_column(String(90), unique=True, nullable=False)

    stats_7d = relationship(
        "WalletStatistic7d",
        back_populates="wallet",
        uselist=False,
    )
    stats_30d = relationship(
        "WalletStatistic30d",
        back_populates="wallet",
        uselist=False,
    )
    stats_all = relationship(
        "WalletStatisticAll",
        back_populates="wallet",
        uselist=False,
    )

    __table_args__ = (
        Index("idx_wallet_created_at", "created_at"),
        Index("idx_wallet_address", "address"),
        Index("idx_wallet_is_bot", "is_bot"),
        Index("idx_wallet_is_scammer", "is_scammer"),
        Index("idx_wallet_last_stats_check", text("last_stats_check NULLS FIRST")),
        Index(
            "wallet_idx_last_activity_last_stats_check",
            "last_activity_timestamp",
            text("last_stats_check NULLS FIRST"),
        ),
    )

    def __str__(self):
        return f"{self.address}"


class AbstractWalletStatistic(Base, WalletFKPKMixin, TimestampsMixin):
    __abstract__ = True

    token_buy_sell_duration_avg: Mapped[Optional[int]] = mapped_column(BigInteger)
    token_buy_sell_duration_median: Mapped[Optional[int]] = mapped_column(BigInteger, index=True)

    total_profit_multiplier: Mapped[Optional[float]] = mapped_column(Float, index=True)
    pnl_lt_minus_dot5_percent: Mapped[Optional[float]] = mapped_column(Float)
    pnl_minus_dot5_0x_percent: Mapped[Optional[float]] = mapped_column(Float)
    pnl_lt_2x_percent: Mapped[Optional[float]] = mapped_column(Float)
    pnl_2x_5x_percent: Mapped[Optional[float]] = mapped_column(Float)
    pnl_gt_5x_percent: Mapped[Optional[float]] = mapped_column(Float)

    total_token: Mapped[Optional[int]] = mapped_column(Integer, index=True)
    total_token_buys: Mapped[Optional[int]] = mapped_column(Integer)
    total_token_sales: Mapped[Optional[int]] = mapped_column(Integer)
    token_with_buy_and_sell: Mapped[Optional[int]] = mapped_column(Integer)
    token_with_buy: Mapped[Optional[int]] = mapped_column(Integer)
    token_sell_without_buy: Mapped[Optional[int]] = mapped_column(Integer)
    token_buy_without_sell: Mapped[Optional[int]] = mapped_column(Integer)
    token_with_sell_amount_gt_buy_amount: Mapped[Optional[int]] = mapped_column(Integer)
    pnl_lt_minus_dot5_num: Mapped[Optional[int]] = mapped_column(Integer)
    pnl_minus_dot5_0x_num: Mapped[Optional[int]] = mapped_column(Integer)
    pnl_lt_2x_num: Mapped[Optional[int]] = mapped_column(Integer)
    pnl_2x_5x_num: Mapped[Optional[int]] = mapped_column(Integer)
    pnl_gt_5x_num: Mapped[Optional[int]] = mapped_column(Integer)

    winrate: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(40, 5), index=True)
    token_avg_profit_usd: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(50, 20), index=True)
    total_token_buy_amount_usd: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(50, 20))
    total_token_sell_amount_usd: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(50, 20))
    total_profit_usd: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(50, 20), index=True)
    token_avg_buy_amount: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(50, 20), index=True)
    token_median_buy_amount: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(50, 20))
    token_first_buy_avg_price_usd: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(50, 20))
    token_first_buy_median_price_usd: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(50, 20), index=True)

    @property
    def total_buys_and_sales_count(self) -> int:
        return (self.total_token_buys or 0) + (self.total_token_sales or 0)


class WalletStatistic7d(AbstractWalletStatistic):
    __tablename__ = "wallet_statistic_7d"

    wallet = relationship(
        "Wallet",
        back_populates="stats_7d",
        uselist=False,
    )

    def __str__(self):
        return "Статистика кошелька за 7д"


class WalletStatistic30d(AbstractWalletStatistic):
    __tablename__ = "wallet_statistic_30d"

    wallet = relationship(
        "Wallet",
        back_populates="stats_30d",
        uselist=False,
    )

    def __str__(self):
        return "Статистика кошелька за 30д"


class WalletStatisticAll(AbstractWalletStatistic):
    __tablename__ = "wallet_statistic_all"

    wallet = relationship(
        "Wallet",
        back_populates="stats_all",
        uselist=False,
    )

    def __str__(self):
        return "Статистика кошелька за все время"


class WalletStatisticBuyPriceGt15k7d(AbstractWalletStatistic):
    __tablename__ = "wallet_statistic_buy_price_gt_15k_7d"

    wallet = relationship(
        "Wallet",
        backref="stats_buy_price_gt_15k_7d",
        uselist=False,
    )

    def __str__(self):
        return "Статистика кошелька за 7д"


class WalletStatisticBuyPriceGt15k30d(AbstractWalletStatistic):
    __tablename__ = "wallet_statistic_buy_price_gt_15k_30d"

    wallet = relationship(
        "Wallet",
        backref="stats_buy_price_gt_15k_30d",
        uselist=False,
    )

    def __str__(self):
        return "Статистика кошелька за 30д"


class WalletStatisticBuyPriceGt15kAll(AbstractWalletStatistic):
    __tablename__ = "wallet_statistic_buy_price_gt_15k_all"

    wallet = relationship(
        "Wallet",
        backref="stats_buy_price_gt_15k_all",
        uselist=False,
    )

    def __str__(self):
        return "Статистика кошелька за все время"


class WalletToken(Base, UUIDIDMixin, TimestampsMixin):
    __tablename__ = "wallet_token"

    wallet_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("wallet.id", ondelete="CASCADE"), sort_order=-999)
    token_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("token.id", ondelete="CASCADE"), sort_order=-999)

    first_buy_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    first_sell_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    last_activity_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    total_profit_percent: Mapped[float] = mapped_column(Float, nullable=True)
    first_buy_sell_duration: Mapped[int] = mapped_column(Integer, nullable=True)
    total_buys_count: Mapped[int] = mapped_column(Integer, default=0)
    total_sales_count: Mapped[int] = mapped_column(Integer, default=0)

    total_swaps_from_txs_with_mt_3_swappers: Mapped[int] = mapped_column(Integer, default=0)
    total_swaps_from_arbitrage_swap_events: Mapped[int] = mapped_column(Integer, default=0)

    total_buy_amount_usd: Mapped[Decimal] = mapped_column(DECIMAL(40, 20), default=0)
    total_buy_amount_token: Mapped[Decimal] = mapped_column(DECIMAL(40, 20), default=0)
    first_buy_price_usd: Mapped[Decimal] = mapped_column(DECIMAL(40, 20), nullable=True)
    total_profit_usd: Mapped[Decimal] = mapped_column(DECIMAL(40, 20), default=0)
    total_sell_amount_usd: Mapped[Decimal] = mapped_column(DECIMAL(40, 20), default=0)
    total_sell_amount_token: Mapped[Decimal] = mapped_column(DECIMAL(40, 20), default=0)
    first_sell_price_usd: Mapped[Decimal] = mapped_column(DECIMAL(40, 20), nullable=True)

    wallet = relationship("Wallet", backref="tokens")
    token = relationship("Token", backref="wallets")

    __table_args__ = (
        UniqueConstraint("wallet_id", "token_id"),  # Составной PK
        Index("idx_wallet_token_wallet_id", "wallet_id"),
        Index("idx_wallet_token_token_id", "token_id"),
    )


class TgSentWallet(Base, WalletFKPKMixin, TimestampsMixin):
    __tablename__ = "tg_sent_wallet"

    wallet = relationship("Wallet", backref="tg_sent")


class WalletFiltered(Base, WalletFKPKMixin):
    __tablename__ = "wallet_filtered"

    wallet = relationship("Wallet", backref="wallet_filtered")


class WalletCopyable(Base, WalletFKPKMixin):
    __tablename__ = "wallet_copyable"

    wallet = relationship("Wallet", backref="wallet_copyable")
