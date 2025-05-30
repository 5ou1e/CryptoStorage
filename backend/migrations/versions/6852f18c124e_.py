"""empty message

Revision ID: 6852f18c124e
Revises: b6b84b1e4dfb
Create Date: 2025-03-17 12:30:01.043468

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "6852f18c124e"
down_revision: Union[str, None] = "b6b84b1e4dfb"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "wallet_token",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("wallet_id", sa.UUID(), nullable=False),
        sa.Column("token_id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("first_buy_timestamp", sa.DateTime(timezone=True), nullable=True),
        sa.Column("first_sell_timestamp", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_activity_timestamp", sa.DateTime(timezone=True), nullable=True),
        sa.Column("total_profit_percent", sa.Float(), nullable=True),
        sa.Column("first_buy_sell_duration", sa.Integer(), nullable=True),
        sa.Column("total_buys_count", sa.Integer(), nullable=False),
        sa.Column("total_sales_count", sa.Integer(), nullable=False),
        sa.Column("total_swaps_from_txs_with_mt_3_swappers", sa.Integer(), nullable=False),
        sa.Column("total_swaps_from_arbitrage_swap_events", sa.Integer(), nullable=False),
        sa.Column("total_buy_amount_usd", sa.DECIMAL(precision=40, scale=20), nullable=False),
        sa.Column("total_buy_amount_token", sa.DECIMAL(precision=40, scale=20), nullable=False),
        sa.Column("first_buy_price_usd", sa.DECIMAL(precision=40, scale=20), nullable=True),
        sa.Column("total_profit_usd", sa.DECIMAL(precision=40, scale=20), nullable=False),
        sa.Column("total_sell_amount_usd", sa.DECIMAL(precision=40, scale=20), nullable=False),
        sa.Column(
            "total_sell_amount_token",
            sa.DECIMAL(precision=40, scale=20),
            nullable=False,
        ),
        sa.Column("first_sell_price_usd", sa.DECIMAL(precision=40, scale=20), nullable=True),
        sa.ForeignKeyConstraint(["token_id"], ["token.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["wallet_id"], ["wallet.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("wallet_id", "token_id"),
    )
    op.create_index("idx_wallet_token_token_id", "wallet_token", ["token_id"], unique=False)
    op.create_index("idx_wallet_token_wallet_id", "wallet_token", ["wallet_id"], unique=False)
    op.drop_index("idx_wallet_detail_is_bot", table_name="wallet_detail")
    op.drop_index("idx_wallet_detail_is_scammer", table_name="wallet_detail")
    op.drop_table("wallet_detail")
    op.drop_constraint("tg_sent_wallet_wallet_id_fkey", "tg_sent_wallet", type_="foreignkey")
    op.create_foreign_key(None, "tg_sent_wallet", "wallet", ["wallet_id"], ["id"], ondelete="CASCADE")
    op.add_column(
        "wallet",
        sa.Column("is_scammer", sa.Boolean(), server_default="false", nullable=False),
    )
    op.add_column(
        "wallet",
        sa.Column("is_bot", sa.Boolean(), server_default="false", nullable=False),
    )
    op.add_column(
        "wallet",
        sa.Column("sol_balance", sa.DECIMAL(precision=50, scale=20), nullable=True),
    )
    op.create_index("idx_wallet_is_bot", "wallet", ["is_bot"], unique=False)
    op.create_index("idx_wallet_is_scammer", "wallet", ["is_scammer"], unique=False)
    op.create_index(
        "idx_wallet_last_stats_check",
        "wallet",
        [sa.literal_column("last_stats_check NULLS FIRST")],
        unique=False,
    )
    op.create_index(
        "wallet_idx_last_activity_last_stats_check",
        "wallet",
        ["last_activity_timestamp", sa.literal_column("last_stats_check NULLS FIRST")],
        unique=False,
    )
    op.drop_constraint(
        "wallet_statistic_30d_wallet_id_fkey",
        "wallet_statistic_30d",
        type_="foreignkey",
    )
    op.create_foreign_key(
        None,
        "wallet_statistic_30d",
        "wallet",
        ["wallet_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.drop_constraint("wallet_statistic_7d_wallet_id_fkey", "wallet_statistic_7d", type_="foreignkey")
    op.create_foreign_key(None, "wallet_statistic_7d", "wallet", ["wallet_id"], ["id"], ondelete="CASCADE")
    op.drop_constraint(
        "wallet_statistic_all_wallet_id_fkey",
        "wallet_statistic_all",
        type_="foreignkey",
    )
    op.create_foreign_key(
        None,
        "wallet_statistic_all",
        "wallet",
        ["wallet_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.drop_constraint(
        "wallet_statistic_buy_price_gt_15k_30d_wallet_id_fkey",
        "wallet_statistic_buy_price_gt_15k_30d",
        type_="foreignkey",
    )
    op.create_foreign_key(
        None,
        "wallet_statistic_buy_price_gt_15k_30d",
        "wallet",
        ["wallet_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.drop_constraint(
        "wallet_statistic_buy_price_gt_15k_7d_wallet_id_fkey",
        "wallet_statistic_buy_price_gt_15k_7d",
        type_="foreignkey",
    )
    op.create_foreign_key(
        None,
        "wallet_statistic_buy_price_gt_15k_7d",
        "wallet",
        ["wallet_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.drop_constraint(
        "wallet_statistic_buy_price_gt_15k_all_wallet_id_fkey",
        "wallet_statistic_buy_price_gt_15k_all",
        type_="foreignkey",
    )
    op.create_foreign_key(
        None,
        "wallet_statistic_buy_price_gt_15k_all",
        "wallet",
        ["wallet_id"],
        ["id"],
        ondelete="CASCADE",
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, "wallet_statistic_buy_price_gt_15k_all", type_="foreignkey")
    op.create_foreign_key(
        "wallet_statistic_buy_price_gt_15k_all_wallet_id_fkey",
        "wallet_statistic_buy_price_gt_15k_all",
        "wallet",
        ["wallet_id"],
        ["id"],
    )
    op.drop_constraint(None, "wallet_statistic_buy_price_gt_15k_7d", type_="foreignkey")
    op.create_foreign_key(
        "wallet_statistic_buy_price_gt_15k_7d_wallet_id_fkey",
        "wallet_statistic_buy_price_gt_15k_7d",
        "wallet",
        ["wallet_id"],
        ["id"],
    )
    op.drop_constraint(None, "wallet_statistic_buy_price_gt_15k_30d", type_="foreignkey")
    op.create_foreign_key(
        "wallet_statistic_buy_price_gt_15k_30d_wallet_id_fkey",
        "wallet_statistic_buy_price_gt_15k_30d",
        "wallet",
        ["wallet_id"],
        ["id"],
    )
    op.drop_constraint(None, "wallet_statistic_all", type_="foreignkey")
    op.create_foreign_key(
        "wallet_statistic_all_wallet_id_fkey",
        "wallet_statistic_all",
        "wallet",
        ["wallet_id"],
        ["id"],
    )
    op.drop_constraint(None, "wallet_statistic_7d", type_="foreignkey")
    op.create_foreign_key(
        "wallet_statistic_7d_wallet_id_fkey",
        "wallet_statistic_7d",
        "wallet",
        ["wallet_id"],
        ["id"],
    )
    op.drop_constraint(None, "wallet_statistic_30d", type_="foreignkey")
    op.create_foreign_key(
        "wallet_statistic_30d_wallet_id_fkey",
        "wallet_statistic_30d",
        "wallet",
        ["wallet_id"],
        ["id"],
    )
    op.drop_index("wallet_idx_last_activity_last_stats_check", table_name="wallet")
    op.drop_index("idx_wallet_last_stats_check", table_name="wallet")
    op.drop_index("idx_wallet_is_scammer", table_name="wallet")
    op.drop_index("idx_wallet_is_bot", table_name="wallet")
    op.drop_column("wallet", "sol_balance")
    op.drop_column("wallet", "is_bot")
    op.drop_column("wallet", "is_scammer")
    op.drop_constraint(None, "tg_sent_wallet", type_="foreignkey")
    op.create_foreign_key(
        "tg_sent_wallet_wallet_id_fkey",
        "tg_sent_wallet",
        "wallet",
        ["wallet_id"],
        ["id"],
    )
    op.create_table(
        "wallet_detail",
        sa.Column("wallet_id", sa.UUID(), autoincrement=False, nullable=False),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column("is_scammer", sa.BOOLEAN(), autoincrement=False, nullable=False),
        sa.Column("is_bot", sa.BOOLEAN(), autoincrement=False, nullable=False),
        sa.Column(
            "sol_balance",
            sa.NUMERIC(precision=50, scale=20),
            autoincrement=False,
            nullable=True,
        ),
        sa.ForeignKeyConstraint(["wallet_id"], ["wallet.id"], name="wallet_detail_wallet_id_fkey"),
        sa.PrimaryKeyConstraint("wallet_id", name="wallet_detail_pkey"),
    )
    op.create_index("idx_wallet_detail_is_scammer", "wallet_detail", ["is_scammer"], unique=False)
    op.create_index("idx_wallet_detail_is_bot", "wallet_detail", ["is_bot"], unique=False)
    op.drop_index("idx_wallet_token_wallet_id", table_name="wallet_token")
    op.drop_index("idx_wallet_token_token_id", table_name="wallet_token")
    op.drop_table("wallet_token")
    # ### end Alembic commands ###
