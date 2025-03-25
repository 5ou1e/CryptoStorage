from celery import Celery

from src.infra.celery.tasks import *
from src.settings import config
from src.settings.logging import setup_celery_logging

setup_celery_logging()

app = Celery("core")


app.conf.broker_url = config.celery.broker_url
app.conf.result_backend = config.celery.result_backend

# Автоматическое обнаружение задач
app.autodiscover_tasks(packages=["src.infra.celery.tasks"])

app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
)


@app.on_after_configure.connect
def setup_tasks_on_startup(sender, **kwargs):
    """Настройка периодических задач Celery при старте воркера."""
    # collect_sol_prices_task.apply_async(task_name="Сбор цены Solana с Binance")
    #
    # update_wallet_statistics_task.apply_async(task_name="Обновление статистик кошельков")
    #
    update_wallet_statistics_buy_price_gt_15k_task.apply_async(task_name="Обновление статистик кошельков Price gt 15k")
    #
    # parse_tokens_metadata_task.apply_async(task_name="Сбор метаданных токенов")
    #
    # send_wallets_in_tg_task.apply_async(task_name="Отправка уведомлений в ТГ-канал с новыми Топ-кошельками")
