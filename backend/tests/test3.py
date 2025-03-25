import asyncio
from datetime import datetime

from sqlalchemy import case, func, select
from sqlalchemy.dialects.postgresql import insert

from src.domain.entities import Token as TokenEntity
from src.domain.entities import Wallet as WalletEntity
from src.domain.entities.wallet import WalletToken
from src.infra.db.sqlalchemy.models import Wallet, WalletToken
from src.infra.db.sqlalchemy.repositories import SQLAlchemyWalletTokenRepository
from src.infra.db.sqlalchemy.setup import engine, get_db_session

wallet_token = WalletToken


async def main():
    print(WalletEntity())
    async for session in get_db_session():
        result = await session.execute(select(WalletEntity).limit(1))
        instance = result.scalars().first()
        print(instance)


asyncio.run(main())
