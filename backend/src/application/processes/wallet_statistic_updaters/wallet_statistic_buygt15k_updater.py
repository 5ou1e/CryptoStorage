import asyncio
import logging
from collections import defaultdict
from datetime import datetime

import pytz

from src.domain.entities import (
    Wallet,
    WalletStatisticBuyPriceGt15k7d,
    WalletStatisticBuyPriceGt15k30d,
    WalletStatisticBuyPriceGt15kAll,
)
from src.domain.entities.wallet import WalletFiltered
from src.infra.db.sqlalchemy.repositories import (
    SQLAlchemyWalletRepository,
    SQLAlchemyWalletStatisticBuyPriceGt15k7dRepository,
    SQLAlchemyWalletStatisticBuyPriceGt15k30dRepository,
    SQLAlchemyWalletStatisticBuyPriceGt15kAllRepository,
    SQLAlchemyWalletTokenRepository,
)
from src.infra.db.sqlalchemy.repositories.wallet import SQLAlchemyWalletFilteredRepository
from src.infra.db.sqlalchemy.setup import AsyncSessionMaker

from .calculations import filter_period_tokens, recalculate_wallet_period_stats

logger = logging.getLogger(__name__)


async def update_wallet_statistics_buygt15k_async():
    wallets = await get_wallets_for_update()
    if wallets:
        await process_wallets(wallets)
    else:
        await delete_old_filtered_wallets()


async def get_wallets_for_update():
    logger.debug(f"Начинаем получение кошельков из БД")
    t1 = datetime.now()
    async with AsyncSessionMaker() as session:
        wallets = await SQLAlchemyWalletRepository(session).get_wallets_for_buygt15k_statistic()
    t2 = datetime.now()
    logger.info(f"Получили {len(wallets)} кошельков из БД | Время: {t2-t1}")
    return wallets


async def process_wallets(wallets):
    """Массовое обновление статистик кошельков на основе их транзакций"""
    start = datetime.now()
    await load_tokens(wallets)
    logger.debug(f"Начинаем подсчет статистики для {len(wallets)} кошельков")
    for wallet in wallets:
        calculate_wallet(wallet)
    logger.debug(f"Посчитали статистику для {len(wallets)} кошельков")

    await delete_old_filtered_wallets()
    await create_new_filtered_wallets(wallets)
    await create_wallet_stats_in_db(wallets)

    end_time = datetime.now()
    elapsed_time = end_time - start

    logger.info(f"Обновили кошельки в базе! Кошельков: {len(wallets)} | Время: {elapsed_time}")


async def load_tokens(wallets):
    async with AsyncSessionMaker() as session:
        wallet_tokens = await SQLAlchemyWalletTokenRepository(
            session
        ).get_wallet_tokens_by_wallets_list_for_buygt15k_statistic([wallet.id for wallet in wallets])
    wt_count = len(wallet_tokens)
    logger.debug(f"Подгрузили токены {len(wallets)} кошельков из БД | Токенов: {wt_count}")

    wallet_tokens_map = defaultdict(list)
    for wt in wallet_tokens:
        wallet_tokens_map[wt.wallet_id].append(wt)
    dt_now = datetime.now(tz=pytz.UTC)
    for wallet in wallets:
        wallet.stats_buy_price_gt_15k_7d = WalletStatisticBuyPriceGt15k7d(
            wallet_id=wallet.id, updated_at=dt_now, created_at=dt_now
        )
        wallet.stats_buy_price_gt_15k_30d = WalletStatisticBuyPriceGt15k30d(
            wallet_id=wallet.id, updated_at=dt_now, created_at=dt_now
        )
        wallet.stats_buy_price_gt_15k_all = WalletStatisticBuyPriceGt15kAll(
            wallet_id=wallet.id, updated_at=dt_now, created_at=dt_now
        )
        wallet.tokens = [wt for wt in wallet_tokens_map[wallet.id]]


async def delete_old_filtered_wallets() -> None:
    async with AsyncSessionMaker() as session:
        await SQLAlchemyWalletFilteredRepository(session).delete_all()
        await session.commit()


async def create_new_filtered_wallets(wallets: list[Wallet]):
    wallets_filtered = [WalletFiltered(wallet_id=wallet.id) for wallet in wallets]
    async with AsyncSessionMaker() as session:
        await SQLAlchemyWalletFilteredRepository(session).bulk_create(wallets_filtered)
        await session.commit()


async def create_wallet_stats_in_db(wallets):
    await asyncio.gather(
        _create_stats_7d([wallet.stats_buy_price_gt_15k_7d for wallet in wallets]),
        _create_stats_30d([wallet.stats_buy_price_gt_15k_30d for wallet in wallets]),
        _create_stats_all([wallet.stats_buy_price_gt_15k_all for wallet in wallets]),
    )
    logger.debug(f"Обновили статистики кошельков")


async def _create_stats_7d(stats):
    async with AsyncSessionMaker() as session:
        await SQLAlchemyWalletStatisticBuyPriceGt15k7dRepository(session).create_or_update(stats)
        await session.commit()


async def _create_stats_30d(stats):
    async with AsyncSessionMaker() as session:
        await SQLAlchemyWalletStatisticBuyPriceGt15k30dRepository(session).create_or_update(stats)
        await session.commit()


async def _create_stats_all(stats):
    async with AsyncSessionMaker() as session:
        await SQLAlchemyWalletStatisticBuyPriceGt15kAllRepository(session).create_or_update(stats)
        await session.commit()


def calculate_wallet(wallet: Wallet):
    recalculate_wallet_stats(wallet)
    logger.debug(f"Посчитали статистику кошелька {wallet.address}")


def recalculate_wallet_stats(wallet: Wallet):
    periods = [7, 30, 0]
    all_tokens = wallet.tokens
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
