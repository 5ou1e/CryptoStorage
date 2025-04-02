from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .common import Base, IntIDMixin, TimestampsMixin, UUIDIDMixin


class User(Base, UUIDIDMixin, TimestampsMixin):
    __tablename__ = "user"

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
        nullable=True,
        default=datetime.utcnow,
    )
    last_login: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=datetime.utcnow,
    )

    class PydanticMeta:
        exclude = ["hashed_password"]


class UserWallet(Base, UUIDIDMixin):
    __tablename__ = "user_wallet"

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"))
    wallet_id: Mapped[int] = mapped_column(ForeignKey("wallet.id", ondelete="CASCADE"))

    is_favorite: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_blacklisted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_watch_later: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    remark: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    user: Mapped["User"] = relationship("User")
    wallet: Mapped["Wallet"] = relationship("Wallet")

    __table_args__ = (UniqueConstraint("user_id", "wallet_id", name="uq_user_wallet"),)
