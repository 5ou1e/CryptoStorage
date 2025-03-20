import asyncio
from datetime import datetime

from sqlalchemy import case, func, select
from sqlalchemy.dialects.postgresql import insert

from src.domain.entities.wallet import WalletTokenEntity
from src.infra.db.models.sqlalchemy import WalletToken
from src.infra.db.repositories.sqlalchemy import SQLAlchemyWalletTokenRepository
from src.infra.db.setup import engine, get_db_session

wallet_token = WalletToken


async def main():
    async for session in get_db_session():
        result = await session.execute(select(WalletToken).limit(1))
        start = datetime.now()
        rows = result.scalars().all()
        rows = [row.__dict__ for row in rows]
        # print(rows)
        for d in rows:
            d.pop("_sa_instance_state", None)
        records = [WalletTokenEntity(**row) for row in rows]
        for record in records:
            record.first_buy_sell_duration = 9999
        repo = SQLAlchemyWalletTokenRepository(session)
        await repo.bulk_create(
            records, ignore_conflicts=False, on_conflict=["id"], update_fields=["first_buy_sell_duration"]
        )
        await session.commit()
        # conn = await session.connection()
        # await conn.execute(stmt, rows)
        # await conn.commit()
        print(datetime.now() - start)


asyncio.run(main())
