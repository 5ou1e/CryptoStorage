from sqlalchemy import Integer, case, cast, extract, func, or_
from sqlalchemy.dialects.postgresql import insert

from src.infra.db.models.sqlalchemy import WalletToken


def get_bulk_update_or_create_wallet_token_with_merge_stmt():
    stmt = insert(WalletToken)
    stmt = stmt.on_conflict_do_update(
        index_elements=["wallet_id", "token_id"],
        set_={
            "total_buys_count": WalletToken.total_buys_count + stmt.excluded.total_buys_count,
            "total_buy_amount_usd": WalletToken.total_buy_amount_usd + stmt.excluded.total_buy_amount_usd,
            "total_buy_amount_token": WalletToken.total_buy_amount_token + stmt.excluded.total_buy_amount_token,
            "first_buy_price_usd": case(
                (
                    (
                        or_(
                            WalletToken.first_buy_timestamp.is_(None),
                            stmt.excluded.first_buy_timestamp < WalletToken.first_buy_timestamp,
                        ),
                        stmt.excluded.first_buy_price_usd,
                    )
                ),
                else_=WalletToken.first_buy_price_usd,
            ),
            "first_buy_timestamp": func.least(WalletToken.first_buy_timestamp, stmt.excluded.first_buy_timestamp),
            "total_sales_count": WalletToken.total_sales_count + stmt.excluded.total_sales_count,
            "total_sell_amount_usd": WalletToken.total_sell_amount_usd + stmt.excluded.total_sell_amount_usd,
            "total_sell_amount_token": WalletToken.total_sell_amount_token + stmt.excluded.total_sell_amount_token,
            "first_sell_price_usd": func.coalesce(WalletToken.first_sell_price_usd, stmt.excluded.first_sell_price_usd),
            "first_sell_timestamp": case(
                (
                    (
                        or_(
                            WalletToken.first_sell_timestamp.is_(None),
                            stmt.excluded.first_sell_timestamp < WalletToken.first_sell_timestamp,
                        ),
                        stmt.excluded.first_sell_timestamp,
                    )
                ),
                else_=WalletToken.first_sell_timestamp,
            ),
            "last_activity_timestamp": func.greatest(
                WalletToken.last_activity_timestamp, stmt.excluded.last_activity_timestamp
            ),
            "total_profit_usd": WalletToken.total_profit_usd + stmt.excluded.total_profit_usd,
            "total_profit_percent": case(
                (
                    WalletToken.total_buy_amount_usd + stmt.excluded.total_buy_amount_usd > 0,
                    (
                        (WalletToken.total_sell_amount_usd + stmt.excluded.total_sell_amount_usd)
                        - (WalletToken.total_buy_amount_usd + stmt.excluded.total_buy_amount_usd)
                    )
                    / (WalletToken.total_buy_amount_usd + stmt.excluded.total_buy_amount_usd)
                    * 100,
                ),
                else_=None,
            ),
            "first_buy_sell_duration": case(
                (
                    func.least(WalletToken.first_buy_timestamp, stmt.excluded.first_buy_timestamp).isnot(None)
                    & func.least(WalletToken.first_sell_timestamp, stmt.excluded.first_sell_timestamp).isnot(None),
                    cast(
                        extract(
                            "epoch",
                            func.least(WalletToken.first_sell_timestamp, stmt.excluded.first_sell_timestamp)
                            - func.least(WalletToken.first_buy_timestamp, stmt.excluded.first_buy_timestamp),
                        ),
                        Integer,
                    ),
                ),
                else_=None,
            ),
            "total_swaps_from_txs_with_mt_3_swappers": WalletToken.total_swaps_from_txs_with_mt_3_swappers
            + stmt.excluded.total_swaps_from_txs_with_mt_3_swappers,
            "total_swaps_from_arbitrage_swap_events": WalletToken.total_swaps_from_arbitrage_swap_events
            + stmt.excluded.total_swaps_from_arbitrage_swap_events,
            "updated_at": func.now(),
        },
    )
    # print(stmt.compile())
    return stmt
