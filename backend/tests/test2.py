import asyncio
from datetime import datetime

from sqlalchemy import case, func, select
from sqlalchemy.dialects.postgresql import insert

from src.domain.entities.wallet import WalletTokenEntity
from src.infra.db.models.sqlalchemy import WalletToken
from src.infra.db.repositories.sqlalchemy import SQLAlchemyWalletTokenRepository
from src.infra.db.setup import get_db_session

wallet_token = WalletToken


async def main():
    async for session in get_db_session():
        result = await session.execute(select(WalletToken).limit(10000))
        start = datetime.now()
        rows = result.scalars().all()
        rows = [row.__dict__ for row in rows]

        # print(rows)
        for d in rows:
            d.pop("_sa_instance_state", None)
        rows = [WalletTokenEntity(**row) for row in rows]
        # return
        # stmt = insert(WalletToken).values(
        #     wallet_id="745a0445-feb9-11ef-ae9c-00155d80116b",
        #     token_id="d4078f5c-febc-11ef-8220-00155d80116b",
        #     total_buys_count=10,
        #     total_buy_amount_usd=100.50,
        #     total_buy_amount_token=500.25,
        #     first_buy_price_usd=10.75,
        #     first_buy_timestamp=1710331200,
        #     total_sales_count=5,
        #     total_sell_amount_usd=200.75,
        #     total_sell_amount_token=700.30,
        #     first_sell_price_usd=12.50,
        #     first_sell_timestamp=1710031500,
        #     last_activity_timestamp=1710331800,
        #     total_profit_usd=50.00,
        #     total_profit_percent=None,
        #     first_buy_sell_duration=None,
        #     total_swaps_from_txs_with_mt_3_swappers=3,
        #     total_swaps_from_arbitrage_swap_events=2,
        # )

        stmt = insert(WalletToken)

        stmt = stmt.on_conflict_do_update(
            index_elements=["wallet_id", "token_id"],
            set_={
                "total_buys_count": WalletToken.__table__.c.total_buys_count + stmt.excluded.total_buys_count,
                "total_buy_amount_usd": WalletToken.__table__.c.total_buy_amount_usd
                + stmt.excluded.total_buy_amount_usd,
                "total_buy_amount_token": WalletToken.__table__.c.total_buy_amount_token
                + stmt.excluded.total_buy_amount_token,
                "first_buy_price_usd": func.coalesce(
                    WalletToken.__table__.c.first_buy_price_usd, stmt.excluded.first_buy_price_usd
                ),
                "first_buy_timestamp": func.least(
                    WalletToken.__table__.c.first_buy_timestamp, stmt.excluded.first_buy_timestamp
                ),
                "total_sales_count": WalletToken.__table__.c.total_sales_count + stmt.excluded.total_sales_count,
                "total_sell_amount_usd": WalletToken.__table__.c.total_sell_amount_usd
                + stmt.excluded.total_sell_amount_usd,
                "total_sell_amount_token": WalletToken.__table__.c.total_sell_amount_token
                + stmt.excluded.total_sell_amount_token,
                "first_sell_price_usd": func.coalesce(
                    WalletToken.__table__.c.first_sell_price_usd, stmt.excluded.first_sell_price_usd
                ),
                "first_sell_timestamp": func.least(
                    WalletToken.__table__.c.first_sell_timestamp, stmt.excluded.first_sell_timestamp
                ),
                "last_activity_timestamp": func.greatest(
                    WalletToken.__table__.c.last_activity_timestamp, stmt.excluded.last_activity_timestamp
                ),
                "total_profit_usd": WalletToken.__table__.c.total_profit_usd + stmt.excluded.total_profit_usd,
                "total_profit_percent": case(
                    (
                        WalletToken.__table__.c.total_buy_amount_usd + stmt.excluded.total_buy_amount_usd > 0,
                        (
                            (WalletToken.__table__.c.total_sell_amount_usd + stmt.excluded.total_sell_amount_usd)
                            - (WalletToken.__table__.c.total_buy_amount_usd + stmt.excluded.total_buy_amount_usd)
                        )
                        / (WalletToken.__table__.c.total_buy_amount_usd + stmt.excluded.total_buy_amount_usd)
                        * 100,
                    ),
                    else_=None,
                ),
                "first_buy_sell_duration": case(
                    (
                        WalletToken.__table__.c.first_buy_timestamp.isnot(None)
                        & WalletToken.__table__.c.first_sell_timestamp.isnot(None),
                        WalletToken.__table__.c.first_sell_timestamp - WalletToken.__table__.c.first_buy_timestamp,
                    ),
                    else_=None,
                ),
                "total_swaps_from_txs_with_mt_3_swappers": WalletToken.__table__.c.total_swaps_from_txs_with_mt_3_swappers
                + stmt.excluded.total_swaps_from_txs_with_mt_3_swappers,
                "total_swaps_from_arbitrage_swap_events": WalletToken.__table__.c.total_swaps_from_arbitrage_swap_events
                + stmt.excluded.total_swaps_from_arbitrage_swap_events,
                "updated_at": func.now(),
            },
        )
        # conn = await session.connection()
        # await conn.execute(stmt, rows)
        # await conn.commit()
        # print(datetime.now()-start)
        #
        conn = await session.connection()
        repo = SQLAlchemyWalletTokenRepository(session)
        await repo.bulk_update_or_create_wallet_token_with_merge(rows)
        print(datetime.now() - start)


asyncio.run(main())
