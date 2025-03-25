import asyncio
import random
from datetime import datetime
from typing import List

import numpy as np
from sqlalchemy import delete, update
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
    # Импортируем активности и статистики обязательно в транзакции!
    await import_activities_and_wallet_tokens(activities, wallet_tokens, end_time)
    logger.info(f"Свапов: {len(activities)}")
    logger.info(f"Кошелек-токен: {len(wallet_tokens)}")


async def import_activities_and_wallet_tokens(
    activities: List[Swap],
    wallet_tokens: List[WalletToken],
    end_time: datetime,
):
    from src.infra.db.sqlalchemy.models import Swap as SwapModel

    async with AsyncSessionLocal() as session:
        BATCH_SIZE = 30000
        target_ids = [activity.id for activity in activities]
        print(f"Удаляем {[a.tx_hash for a in activities[:10]]} ...")

        for i in range(0, len(target_ids), BATCH_SIZE):
            chunk = target_ids[i : i + BATCH_SIZE]
            await session.execute(delete(SwapModel).where(SwapModel.id.in_(chunk)))
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
