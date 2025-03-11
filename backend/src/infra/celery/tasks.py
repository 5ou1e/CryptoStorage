import asyncio
import logging

from celery import shared_task

from src.application.etl.sol_prices_collector import (
    collect_prices_async,
)
from src.application.etl.tg_wallets_sender import (
    send_wallets_in_tg_async,
)
from src.application.etl.tokens_metadata_parser import (
    parse_tokens_metadata_async,
)
from src.application.etl.wallet_statistic_buygt15k_update_manager import (
    update_wallet_statistics_buygt15k_async,
)
from src.application.etl.wallet_statistic_update_manager import (
    process_update_wallet_statistics,
    update_single_wallet_statistics,
)
from src.infra.celery.task_logger import (
    task_logger,
)
from src.settings import config


@shared_task
@task_logger(logger=logging.getLogger("tasks.collect_sol_prices"))
def collect_sol_prices_task():
    # Задача сбора цен Solana
    asyncio.run(collect_prices_async())
    c = config.celery.tasks.collect_sol_prices_task_interval
    collect_sol_prices_task.apply_async(countdown=c)


@shared_task(bind=True, ignore_result=False)
@task_logger(logger=logging.getLogger("tasks.parse_tokens_metadata"))
def parse_tokens_metadata_task(self):
    """Задача сбора метаданных для токенов"""
    asyncio.run(parse_tokens_metadata_async())
    c = config.celery.tasks.parse_tokens_metadata_task
    parse_tokens_metadata_task.apply_async(countdown=c)


@shared_task(bind=True, ignore_result=False)
@task_logger(logger=logging.getLogger("tasks.send_wallets_in_tg"))
def send_wallets_in_tg_task(self):
    """Задача отправки тг-уведомлений с кошельками"""
    asyncio.run(send_wallets_in_tg_async())
    c = config.celery.tasks.send_wallets_in_tg_task_interval
    send_wallets_in_tg_task.apply_async(countdown=c)


@shared_task(bind=True, ignore_result=False)
@task_logger(logger=logging.getLogger("tasks.update_wallet_statistics"))
def update_wallet_statistics_task(self):
    """Задача обновления статистики кошельков"""
    asyncio.run(process_update_wallet_statistics())


@shared_task(bind=True, ignore_result=False)
@task_logger(logger=logging.getLogger("tasks.update_wallet_statistics"))
def update_single_wallet_statistics_task(self, wallet_id):
    """Задача обновления статистики конкретного кошелька"""
    asyncio.run(update_single_wallet_statistics(wallet_id))


@shared_task(bind=True, ignore_result=False)
@task_logger(logger=logging.getLogger("tasks.update_wallet_statistics_buy_price_gt_15k"))
def update_wallet_statistics_buy_price_gt_15k_task(
    self,
):
    """Задача обновления статистики кошельков с ценой покупки токена более 15к"""
    asyncio.run(update_wallet_statistics_buygt15k_async())
    countdown = config.celery.tasks.update_wallet_statistics_buy_price_gt_15k_task_interval
    update_wallet_statistics_buy_price_gt_15k_task.apply_async(countdown=countdown)
