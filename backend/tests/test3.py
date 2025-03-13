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
    repo = TortoiseWalletStatistic7dRepository()
    stats = await repo.get_list(limit=10000)
    await repo.bulk_update(stats, id_column='wallet_id')


asyncio.run(main())
