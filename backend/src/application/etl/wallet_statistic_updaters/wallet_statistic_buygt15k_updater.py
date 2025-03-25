import asyncio
import logging
from asyncio import Semaphore
from datetime import datetime

import pytz

from src.domain.entities import (
    Wallet,
    WalletStatisticBuyPriceGt15k7d,
    WalletStatisticBuyPriceGt15k30d,
    WalletStatisticBuyPriceGt15kAll,
    WalletToken,
)
from src.infra.db.sqlalchemy.repositories import (
    SQLAlchemyWalletRepository,
    SQLAlchemyWalletStatisticBuyPriceGt15k7dRepository,
    SQLAlchemyWalletStatisticBuyPriceGt15k30dRepository,
    SQLAlchemyWalletStatisticBuyPriceGt15kAllRepository,
    SQLAlchemyWalletTokenRepository,
)
from src.infra.db.sqlalchemy.setup import AsyncSessionLocal

from .calculations import filter_period_tokens, recalculate_wallet_period_stats

logger = logging.getLogger("tasks.update_wallet_statistics")


async def update_wallet_statistics_buygt15k_async():
    async with AsyncSessionLocal() as session:
        await SQLAlchemyWalletStatisticBuyPriceGt15k7dRepository(session).delete_all()
        await SQLAlchemyWalletStatisticBuyPriceGt15k30dRepository(session).delete_all()
        await SQLAlchemyWalletStatisticBuyPriceGt15kAllRepository(session).delete_all()
        await session.commit()
    wallets = await get_wallets_for_update()
    if wallets:
        await process_wallets(wallets)


async def get_wallets_for_update():
    logger.debug(f"Начинаем получение кошельков из БД")
    t1 = datetime.now()
    async with AsyncSessionLocal() as session:
        wallets = await SQLAlchemyWalletRepository(session).get_wallets_for_buygt15k_statistic()
    t2 = datetime.now()
    logger.info(f"Получили {len(wallets)} кошельков из БД | Время: {t2-t1}")
    return wallets


async def process_wallets(wallets):
    """Массовое обновление статистик кошельков на основе их транзакций"""
    start = datetime.now()
    wallets_count = len(wallets)

    logger.debug(f"Начинаем подсчет статистики для {wallets_count} кошельков")
    semaphore = Semaphore(10)
    tasks = [calculate_wallet(wallet, semaphore) for wallet in wallets]
    await asyncio.gather(*tasks)

    logger.debug(f"Посчитали статистику для {wallets_count} кошельков")

    await update_wallet_stats_in_db(wallets)

    end_time = datetime.now()
    elapsed_time = end_time - start

    logger.info(f"Обновили кошельки в базе! Кошельков: {wallets_count} | Время: {elapsed_time}")


async def update_wallet_stats_in_db(wallets):
    await asyncio.gather(
        _update_stats_7d([wallet.stats_buy_price_gt_15k_7d for wallet in wallets]),
        _update_stats_30d([wallet.stats_buy_price_gt_15k_30d for wallet in wallets]),
        _update_stats_all([wallet.stats_buy_price_gt_15k_all for wallet in wallets]),
    )
    logger.debug(f"Обновили статистики кошельков")


async def _update_stats_7d(stats):
    async with AsyncSessionLocal() as session:
        await SQLAlchemyWalletStatisticBuyPriceGt15k7dRepository(session).bulk_create(stats)
        await session.commit()


async def _update_stats_30d(stats):
    async with AsyncSessionLocal() as session:
        await SQLAlchemyWalletStatisticBuyPriceGt15k30dRepository(session).bulk_create(stats)
        await session.commit()


async def _update_stats_all(stats):
    async with AsyncSessionLocal() as session:
        await SQLAlchemyWalletStatisticBuyPriceGt15kAllRepository(session).bulk_create(stats)
        await session.commit()


async def calculate_wallet(wallet: Wallet, semaphore):
    dt_now = datetime.now(tz=pytz.UTC)
    async with semaphore:
        wallet.stats_buy_price_gt_15k_7d = WalletStatisticBuyPriceGt15k7d(
            wallet_id=wallet.id, updated_at=dt_now, created_at=dt_now
        )
        wallet.stats_buy_price_gt_15k_30d = WalletStatisticBuyPriceGt15k30d(
            wallet_id=wallet.id, updated_at=dt_now, created_at=dt_now
        )
        wallet.stats_buy_price_gt_15k_all = WalletStatisticBuyPriceGt15kAll(
            wallet_id=wallet.id, updated_at=dt_now, created_at=dt_now
        )
        async with AsyncSessionLocal() as session:
            wallet_tokens = await SQLAlchemyWalletTokenRepository(
                session
            ).get_wallet_tokens_by_wallet_for_buygt15k_statistic(wallet_id=wallet.id)
        logger.debug(f"Получили токен-статы кошелька {wallet.address}")
        recalculate_wallet_stats(wallet, wallet_tokens)
        logger.debug(f"Посчитали статистику кошелька {wallet.address}")


def recalculate_wallet_stats(wallet: Wallet, all_tokens: list[WalletToken]):
    periods = [7, 30, 0]
    current_datetime = datetime.now().astimezone(tz=pytz.UTC)
    for period in periods:
        if period == 7:
            stats = wallet.stats_buy_price_gt_15k_7d
        elif period == 30:
            stats = wallet.stats_buy_price_gt_15k_30d
        else:
            stats = wallet.stats_buy_price_gt_15k_all
        token_stats = filter_period_tokens(all_tokens, period, current_datetime)
        recalculate_wallet_period_stats(stats, token_stats)
