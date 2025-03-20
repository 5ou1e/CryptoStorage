import asyncio
import logging
from asyncio import Semaphore
from datetime import datetime

import pytz
from tortoise import Tortoise

from src.infra.db.models.tortoise import (
    Wallet,
    WalletStatisticBuyPriceGt15k7d,
    WalletStatisticBuyPriceGt15k30d,
    WalletStatisticBuyPriceGt15kAll,
    WalletToken,
)
from src.infra.db.repositories.tortoise import (
    TortoiseWalletStatisticBuyPriceGt15k7dRepository,
    TortoiseWalletStatisticBuyPriceGt15k30dRepository,
    TortoiseWalletStatisticBuyPriceGt15kAllRepository,
)
from src.infra.db.setup_tortoise import init_db_async

from .calculations import filter_period_tokens, recalculate_wallet_period_stats

logger = logging.getLogger("tasks.update_wallet_statistics")


async def update_wallet_statistics_buygt15k_async():
    try:
        await init_db_async()
        await WalletStatisticBuyPriceGt15k7d.all().delete()
        await WalletStatisticBuyPriceGt15k30d.all().delete()
        await WalletStatisticBuyPriceGt15kAll.all().delete()
        wallets = await get_wallets_for_update()
        if wallets:
            await process_wallets(wallets)
    finally:
        await Tortoise.close_connections()


async def get_wallets_for_update():
    logger.debug(f"Начинаем получение кошельков из БД")
    t1 = datetime.now()
    wallets = (
        await Wallet.filter(
            stats_all__winrate__gte=30,
            stats_all__total_profit_usd__gte=3000,
            stats_all__total_profit_multiplier__gte=30,
            stats_all__total_token__gte=4,
            stats_all__token_avg_buy_amount__gte=150,
            stats_all__token_avg_buy_amount__lte=800,
            stats_all__token_buy_sell_duration_median__gte=60,
            stats_30d__total_token__gte=1,
            is_scammer=False,
            is_bot=False,
        )
        .prefetch_related(
            "stats_buy_price_gt_15k_7d",
            "stats_buy_price_gt_15k_30d",
            "stats_buy_price_gt_15k_all",
        )
        .all()
    )
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
    results = await asyncio.gather(*tasks)

    total_wallet_token_stats_count = sum([wt_stats_count for wt_stats_count in results])

    logger.debug(f"Посчитали статистику для {wallets_count} кошельков")
    logger.debug(f"Всего токен-статистик - {total_wallet_token_stats_count}")

    await update_wallet_stats_in_db(wallets)

    end_time = datetime.now()
    elapsed_time = end_time - start

    logger.info(
        f"Обновили кошельки в базе! Кошельков: {wallets_count} | "
        f"Токен-статистик: {total_wallet_token_stats_count} | Время: {elapsed_time} "
    )


async def update_wallet_stats_in_db(wallets):
    wallet_stats_7d = [wallet._stats_buy_price_gt_15k_7d for wallet in wallets]
    wallet_stats_30d = [wallet._stats_buy_price_gt_15k_30d for wallet in wallets]
    wallet_stats_all = [wallet._stats_buy_price_gt_15k_all for wallet in wallets]
    await asyncio.gather(
        TortoiseWalletStatisticBuyPriceGt15k7dRepository().bulk_update(wallet_stats_7d),
        TortoiseWalletStatisticBuyPriceGt15k30dRepository().bulk_update(wallet_stats_30d),
        TortoiseWalletStatisticBuyPriceGt15kAllRepository().bulk_update(wallet_stats_all),
    )
    logger.debug(f"Обновили статистики кошельков за периоды")


async def calculate_wallet(wallet, semaphore):
    async with semaphore:
        stats_instance = await WalletStatisticBuyPriceGt15k7d.create(
            wallet_id=wallet.id,
        )
        wallet._stats_buy_price_gt_15k_7d = stats_instance
        stats_instance = await WalletStatisticBuyPriceGt15k30d.create(
            wallet_id=wallet.id,
        )
        wallet._stats_buy_price_gt_15k_30d = stats_instance
        stats_instance = await WalletStatisticBuyPriceGt15kAll.create(
            wallet_id=wallet.id,
        )
        wallet._stats_buy_price_gt_15k_all = stats_instance
        wallet_token_stats = await WalletToken.filter(
            wallet=wallet,
            first_buy_price_usd__gte=0.000008,
            total_buy_amount_usd__gte=100,
        ).all()
        wallet_token_stats_count = len(wallet_token_stats)
        logger.debug(f"Получили токен-статы кошелька {wallet.address}, всего - {wallet_token_stats_count}")
        recalculate_wallet_stats(wallet, wallet_token_stats)
        logger.debug(f"Посчитали статистику кошелька {wallet.address} в базу")

        return wallet_token_stats_count


def recalculate_wallet_stats(wallet, all_tokens):
    periods = [7, 30, 0]
    current_datetime = datetime.now().astimezone(tz=pytz.UTC)
    for period in periods:
        if period == 7:
            stats = wallet._stats_buy_price_gt_15k_7d
        elif period == 30:
            stats = wallet._stats_buy_price_gt_15k_30d
        else:
            stats = wallet._stats_buy_price_gt_15k_all
        token_stats = filter_period_tokens(all_tokens, period, current_datetime)
        recalculate_wallet_period_stats(stats, token_stats)
