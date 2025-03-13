import asyncio
import random
from datetime import datetime

import numpy as np
from sqlalchemy import text
from tortoise.timezone import now
from tortoise.transactions import in_transaction

from src.infra.db.models.tortoise import Token, Wallet

from src.infra.db.repositories.tortoise import TortoiseTokenRepository
from src.infra.db.repositories.tortoise.wallet import (
    TortoiseWalletStatistic7dRepository,
    TortoiseWalletStatistic30dRepository,
    TortoiseWalletStatisticAllRepository,
    TortoiseWalletRepository,
)
from src.infra.db.setup import get_db_session

from src.infra.db.setup_tortoise import init_db_async


async def main():
    await init_db_async()
    results = await asyncio.gather(
        *[update() for i in range(1)])


async def update():
    repo = TortoiseWalletRepository()
    wallets = []
    for i in range(1):
        limit = random.randint(1,1)
        offset = 500*random.randint(0,10)
        # print(limit, offset)
        w = await Wallet.filter().all().limit(limit).offset(offset)
        wallets.extend(w)
    print(len(wallets))
    wallets = list({wallet.id: wallet for wallet in wallets}.values())
    print(len(wallets))
    wallets.sort(key=lambda w: w.address)
    # random.shuffle(wallets)
    dt = now()
    for wallet in wallets:
        wallet.updated_at = dt
    await repo.bulk_update(wallets, fields=['updated_at'])
    print("Обновили")


async def update1():
    repo = TortoiseWalletRepository()
    wallets = []
    for i in range(10):
        limit = random.randint(500,2000)
        offset = 500*random.randint(0,10)
        # print(limit, offset)
        w = await Wallet.filter().all().limit(limit).offset(offset)
        wallets.extend(w)
    print(len(wallets))
    wallets = list({wallet.id: wallet for wallet in wallets}.values())
    print(len(wallets))
    wallets.sort(key=lambda w: w.address)
    # random.shuffle(wallets)
    dt = now()
    for wallet in wallets:
        wallet.updated_at = dt
    query, params = await repo.bulk_update(wallets[:1], fields=['updated_at'])
    async for session in get_db_session():
        result = await session.execute(text(query), {"values": params})
    print("Обновили")

asyncio.run(main())
