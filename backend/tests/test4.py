import asyncio
import uuid
from datetime import datetime, timedelta
from decimal import Decimal

import uuid6
from sqlalchemy import UniqueConstraint, case, func, inspect, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import class_mapper

from src.application.etl.swaps_loader.loader import (
    import_activities_and_wallet_tokens,
    import_wallets_data_chunk,
)
from src.domain.entities.swap import Swap
from src.domain.entities.wallet import Wallet, WalletToken
from src.infra.db.sqlalchemy.models import Wallet, WalletToken
from src.infra.db.sqlalchemy.repositories import SQLAlchemyWalletRepository, SQLAlchemyWalletTokenRepository
from src.infra.db.sqlalchemy.setup import engine, get_db_session

wallet_token = WalletToken


async def main():
    # columns = class_mapper(wallet_token).columns
    # print(columns)
    # print(columns['wallet_id'].server_default)
    async for session in get_db_session():
        repo = SQLAlchemyWalletRepository(session)
        created_at = datetime.now()

        wallets = [
            Wallet(
                id=uuid6.uuid7(),
                address=str(uuid6.uuid7()),
                created_at=created_at,
                updated_at=created_at,
            )
            for i in range(32000)
        ]
        start = datetime.now()
        res = await repo.bulk_create(wallets)
        # results = res.fetchall()
        # dct = {}
        # for r in results:
        #     dct[r.address] = r

        lst = [wallet.address for wallet in wallets]
        k = await repo.in_bulk(lst, field_name="address")
        print(list(k.values())[0])
        end = datetime.now()
        print(end - start)


async def main1():
    # columns = class_mapper(wallet_token).columns
    # print(columns)
    # print(columns['wallet_id'].server_default)
    async for session in get_db_session():
        created_at = datetime.now()
        activities = [
            Swap(
                id=uuid6.uuid7(),
                wallet_id="00006364-feec-11ef-91ea-00155d80116b",
                token_id="0000c588-feec-11ef-841f-00155d80116b",
                created_at=created_at,
                updated_at=created_at,
            )
            for i in range(1000000)
        ]
        await import_activities_and_wallet_tokens(activities, {})


async def main2():
    async for session in get_db_session():
        created_at = datetime.now()
        repo = SQLAlchemyWalletTokenRepository(session)
        # wallet_tokens = await repo.get_list(limit=10000)

        wallet_tokens = [
            WalletToken(
                wallet_id="01959bad-4d11-7d9d-b6e1-0f31e48b92a5",
                token_id="01959b91-01f2-75cb-837f-f88b8be51f69",
                created_at=datetime.now(),
                updated_at=datetime.now(),
                first_buy_timestamp=datetime.now() - timedelta(minutes=110000),
                first_buy_price_usd=Decimal("11"),
                total_sales_count=1000,
                total_buy_amount_usd=Decimal("1000"),
                total_sell_amount_usd=Decimal("2000"),
                total_profit_usd=Decimal("100099"),
            )
        ]
        start = datetime.now()
        await SQLAlchemyWalletTokenRepository(session).bulk_update_or_create_wallet_token_with_merge(
            wallet_tokens, batch_size=20000
        )
        await session.commit()
        end = datetime.now()
        print(end - start)


async def main1():

    async for session in get_db_session():
        field_name = "address"
        if hasattr(Wallet, field_name):
            column = getattr(Wallet, field_name).property.columns[0]
            print(column)
            if column.unique or column.primary_key:
                print("ok")

        return
        created_at = datetime.now()
        repo = SQLAlchemyWalletTokenRepository(session)
        wallet_tokens = await repo.get_list(limit=100000)

        start = datetime.now()
        fields_to_update = WalletToken.__table__.columns.keys()
        fields_to_update = [
            field for field in fields_to_update if field not in {"id", "wallet_id", "token_id", "created_at"}
        ]
        await SQLAlchemyWalletTokenRepository(session).bulk_create(
            wallet_tokens, batch_size=20000, on_conflict=["wallet_id", "token_id"], update_fields=fields_to_update
        )
        await session.commit()
        end = datetime.now()
        print(end - start)


asyncio.run(main())
