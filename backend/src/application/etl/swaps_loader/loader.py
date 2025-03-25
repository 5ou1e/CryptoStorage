import asyncio
import random
from datetime import datetime
from typing import List

import numpy as np
from sqlalchemy import update
from sqlalchemy.exc import DBAPIError

from src.domain.entities.swap import Swap
from src.domain.entities.token import Token
from src.domain.entities.wallet import (
    Wallet,
    WalletToken,
)
from src.infra.db.sqlalchemy.models import (
    FlipsideConfig,
)
from src.infra.db.sqlalchemy.repositories import (
    SQLAlchemySwapRepository,
    SQLAlchemyTokenRepository,
    SQLAlchemyWalletRepository,
    SQLAlchemyWalletStatistic7dRepository,
    SQLAlchemyWalletStatistic30dRepository,
    SQLAlchemyWalletStatisticAllRepository,
    SQLAlchemyWalletTokenRepository,
)
from src.infra.db.sqlalchemy.repositories.flipside import SQLAlchemyFlipsideConfigRepositoryInterface
from src.infra.db.sqlalchemy.setup import AsyncSessionLocal

from . import config
from .common import utils
from .common.logger import logger


async def load_data_to_db(wallets, tokens, activities, wallet_tokens, end_time) -> None:
    created_wallets_map, created_tokens_map = await asyncio.gather(
        import_wallets_data(wallets),
        import_tokens(tokens),
    )

    for activity in activities:
        activity.wallet_id = created_wallets_map[activity.wallet_address].id
        activity.token_id = created_tokens_map[activity.token_address].id
    for wallet_token in wallet_tokens:
        wallet_token.wallet_id = created_wallets_map[wallet_token.wallet_address].id
        wallet_token.token_id = created_tokens_map[wallet_token.token_address].id

    # Импортируем активности и статистики обязательно в транзакции!
    await import_activities_and_wallet_tokens(activities, wallet_tokens, end_time)

    logger.info(f"Свапов: {len(activities)}")
    logger.info(f"Кошельков: {len(wallets)}")
    logger.info(f"Токенов: {len(tokens)}")
    logger.info(f"Кошелек-токен: {len(wallet_tokens)}")


async def import_wallets_data(wallets, chunks_count=10) -> dict[str, Wallet]:
    """Создаем кошельки и все их связи в несколько тасков"""
    chunks = np.array_split(wallets, chunks_count)
    results = await asyncio.gather(*[import_wallets_data_chunk(chunks[i].tolist()) for i in range(chunks_count)])
    logger.info(f"Кошельки импортированы")
    return {key: value for result in results for key, value in result.items()}


async def import_wallets_data_chunk(
    wallets,
) -> dict[str, Wallet]:
    """Импортируем кошельки со всеми связями в одной транзакции"""
    async with AsyncSessionLocal() as session:
        repository = SQLAlchemyWalletRepository(session)
        # # !!!Сортируем по адресу, чтобы избежать дедлоков при массовом апдейте
        # wallets.sort(key=lambda w: w.address)

        for i in range(5):
            try:
                # В случае конфликта, обновляем метки активностей
                await repository.bulk_create(
                    objects=wallets,
                    on_conflict=["address"],
                    update_fields=[
                        # "first_activity_timestamp",
                        "last_activity_timestamp",
                        "updated_at",
                    ],
                )
                break
            except DBAPIError as e:
                logger.error(f"Deadlock при обновлении кошельков: {e}")
                await asyncio.sleep(random.randint(1, 3))
        else:
            raise ValueError("Не удалось обновить кошельки после 5 попыток")

        created_addresses = list({wallet.address for wallet in wallets})
        created_wallets_map = await repository.in_bulk(created_addresses, "address")

        wallet_stats_7d = []
        wallet_stats_30d = []
        wallet_stats_all = []

        for wallet in wallets:
            # Обновляем айдишники у связей на реальные
            created_wallet_id = created_wallets_map[wallet.address].id
            wallet.stats_7d.wallet_id = created_wallet_id
            wallet.stats_30d.wallet_id = created_wallet_id
            wallet.stats_all.wallet_id = created_wallet_id

            wallet_stats_7d.append(wallet.stats_7d)
            wallet_stats_30d.append(wallet.stats_30d)
            wallet_stats_all.append(wallet.stats_all)

        await SQLAlchemyWalletStatistic7dRepository(session).bulk_create(wallet_stats_7d, ignore_conflicts=True)
        await SQLAlchemyWalletStatistic30dRepository(session).bulk_create(wallet_stats_30d, ignore_conflicts=True)
        await SQLAlchemyWalletStatisticAllRepository(session).bulk_create(wallet_stats_all, ignore_conflicts=True)

        await session.commit()

        return created_wallets_map


async def import_tokens(tokens) -> dict[str, Token]:
    async with AsyncSessionLocal() as session:
        repository = SQLAlchemyTokenRepository(session)
        await repository.bulk_create(tokens, ignore_conflicts=True)
        created_addresses = list({token.address for token in tokens})
        created_tokens_map = await repository.in_bulk(created_addresses, "address")
        await session.commit()
        logger.info("Токены импортированы")
        return created_tokens_map


async def import_activities_and_wallet_tokens(
    activities: List[Swap],
    wallet_tokens: List[WalletToken],
    end_time: datetime,
):
    async with AsyncSessionLocal() as session:
        await SQLAlchemySwapRepository(session).bulk_create(activities, batch_size=500000)
        await SQLAlchemyWalletTokenRepository(session).bulk_update_or_create_wallet_token_with_merge(
            wallet_tokens, batch_size=20000
        )
        if config.PERSISTENT_MODE:
            flipside_cfg = await utils.get_flipside_config()
            flipside_cfg.swaps_parsed_until_block_timestamp = end_time
            await SQLAlchemyFlipsideConfigRepositoryInterface(session).update_swaps_parsed_untill_timestamp(
                flipside_cfg
            )
        await session.commit()
        logger.info(f"Активности и WalletToken импортированы")
