import asyncio
import logging
from functools import wraps

from celery import shared_task

from src.application.processes.sol_prices_collector import collect_prices_async
from src.application.processes.tg_wallets_sender import send_wallets_in_tg_async
from src.application.processes.tokens_metadata_parser import parse_tokens_metadata_async
from src.application.processes.wallet_statistic_updaters.wallet_statistic_buygt15k_updater import (
    update_wallet_statistics_buygt15k_async,
)
from src.application.processes.wallet_statistic_updaters.wallet_statistic_copyable_updater import (
    update_wallet_statistics_copyable_async,
)
from src.application.processes.wallet_statistic_updaters.wallet_statistic_updater import (
    process_update_wallet_statistics,
    update_single_wallet_statistics,
)
from src.infra.celery.logging import setup_task_logging
from src.settings import config


def task_logger(task_func):
    @wraps(task_func)
    def wrapper(*args, **kwargs):
        task_name = task_func.__name__
        setup_task_logging(task_name)
        logger = logging.getLogger(__name__)

        logger.info(f"Запущена задача {task_name}!")

        try:
            return task_func(*args, **kwargs)
        except Exception as e:
            logger.critical(
                f"Ошибка во время выполнения задачи {task_name}!\n{e}",
                exc_info=True,
            )
            raise

    return wrapper


@shared_task
@task_logger
def collect_sol_prices_task():
    # Задача сбора цен Solana
    loop = asyncio.get_event_loop()
    loop.run_until_complete(collect_prices_async())
    c = config.celery.tasks.collect_sol_prices_task_interval
    collect_sol_prices_task.apply_async(countdown=c)


@shared_task(bind=True, ignore_result=False)
@task_logger
def parse_tokens_metadata_task(self):
    """Задача сбора метаданных для токенов"""
    loop = asyncio.get_event_loop()
    loop.run_until_complete(parse_tokens_metadata_async())
    c = config.celery.tasks.parse_tokens_metadata_task
    parse_tokens_metadata_task.apply_async(countdown=c)


@shared_task(bind=True, ignore_result=False)
@task_logger
def send_wallets_in_tg_task(self):
    """Задача отправки тг-уведомлений с кошельками"""
    loop = asyncio.get_event_loop()
    loop.run_until_complete(send_wallets_in_tg_async())
    c = config.celery.tasks.send_wallets_in_tg_task_interval
    send_wallets_in_tg_task.apply_async(countdown=c)


@shared_task(bind=True, ignore_result=False)
@task_logger
def update_wallet_statistics_task(self):
    """Задача обновления статистики кошельков"""
    loop = asyncio.get_event_loop()
    loop.run_until_complete(process_update_wallet_statistics())


@shared_task(bind=True, ignore_result=False)
@task_logger
def update_single_wallet_statistics_task(self, address):
    """Задача обновления статистики конкретного кошелька"""
    # return asyncio.run(update_single_wallet_statistics(address))
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(update_single_wallet_statistics(address))


@shared_task(bind=True, ignore_result=False)
@task_logger
def update_wallet_statistics_buy_price_gt_15k_task(
    self,
):
    """Задача обновления статистики кошельков с ценой покупки токена более 15к"""
    loop = asyncio.get_event_loop()
    loop.run_until_complete(update_wallet_statistics_buygt15k_async())
    countdown = config.celery.tasks.update_wallet_statistics_buy_price_gt_15k_task_interval
    update_wallet_statistics_buy_price_gt_15k_task.apply_async(countdown=countdown)


@shared_task(bind=True, ignore_result=False)
@task_logger
def update_wallet_statistics_copyable_task(
    self,
):
    loop = asyncio.get_event_loop()
    """Задача обновления статистики кошельков копируемых"""
    loop.run_until_complete(update_wallet_statistics_copyable_async())
    countdown = 86400
    update_wallet_statistics_copyable_task.apply_async(countdown=countdown)
