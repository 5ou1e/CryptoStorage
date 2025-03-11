import asyncio
from dataclasses import asdict, dataclass
from datetime import datetime

import numpy as np
from sqlalchemy import select
from tortoise.timezone import now

from src.infra.db.models.tortoise import Wallet
from src.infra.db.models.tortoise import Token
from src.infra.db.models.tortoise.wallet import WalletStatistic, WalletStatistic30d, WalletStatistic7d, \
    WalletStatisticAll
from src.infra.db.repositories.tortoise import TortoiseTokenRepository
from src.infra.db.repositories.tortoise.wallet import TortoiseWalletStatisticRepository, \
    TortoiseWalletStatistic7dRepository, TortoiseWalletStatistic30dRepository, TortoiseWalletStatisticAllRepository
from src.infra.db.setup import get_db_session
from src.infra.db.setup_tortoise import init_db_async


async def main():
    await init_db_async()
    model = WalletStatistic
    repo = TortoiseWalletStatisticRepository()
    stats_list = await model.all().limit(10000).offset(5000)
    for stats in stats_list:
        stats.updated_at = now()
    print("Получили stats")
    start = datetime.now()
    excluded_fields = {"created_at", "wallet_id"}
    fields = set(model._meta.db_fields)
    fields_to_update = list(fields - excluded_fields)  # Поля для обновления
    print("Начинаем загрузку")
    # await repo.bulk_update(
    #     stats_list[:10000],
    #     fields=fields_to_update,
    #     # ignore_conflicts=True
    # )
    chunks_count = 1
    chunks = np.array_split(stats_list, chunks_count)
    results = await asyncio.gather(*[
        repo.bulk_update(chunks[i].tolist()) for i in range(chunks_count)
    ])
    end = datetime.now()
    print(end-start)


async def main1():
    await init_db_async()
    model = WalletStatistic7d
    stats_all = await WalletStatistic7d.all().limit(5000).offset(5000)
    stats_30 = await WalletStatistic30d.all().limit(5000).offset(5000)
    stats_7 = await WalletStatisticAll.all().limit(5000).offset(5000)
    for stats in stats_all:
        stats.updated_at = now()
    for stats in stats_7:
        stats.updated_at = now()
    for stats in stats_30:
        stats.updated_at = now()
    print("Получили stats")
    start = datetime.now()
    excluded_fields = {"created_at", "wallet_id"}
    fields = set(model._meta.db_fields)
    fields_to_update = list(fields - excluded_fields)  # Поля для обновления
    print("Начинаем загрузку")
    await asyncio.gather(
        *[
            TortoiseWalletStatistic7dRepository().bulk_update(
                stats_7,
                fields=fields_to_update,
                # ignore_conflicts=True
            ),
            TortoiseWalletStatistic30dRepository().bulk_update(
                stats_30,
                fields=fields_to_update,
                # ignore_conflicts=True
            ),
            TortoiseWalletStatisticAllRepository().bulk_update(
                stats_all,
                fields=fields_to_update,
                # ignore_conflicts=True
            )
        ]
    )
    end = datetime.now()
    print(end-start)


asyncio.run(main())
