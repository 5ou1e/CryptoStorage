from src.infra.celery.setup import app
from src.infra.celery.tasks import *


@app.on_after_configure.connect
def setup_tasks_on_startup(sender, **kwargs):
    """Настройка периодических задач Celery при старте воркера."""
    # collect_sol_prices_task.apply_async(task_name="Сбор цены Solana с Binance")
    #
    # update_wallet_statistics_task.apply_async(
    #     task_name="Обновление статистик кошельков"
    # )
    #
    # update_wallet_statistics_buy_price_gt_15k_task.apply_async(task_name="Обновление статистик кошельков Price gt 15k")
    #
    update_wallet_statistics_copyable_task.apply_async(task_name="Обновление статистик кошельков copy-traders")

    # parse_tokens_metadata_task.apply_async(task_name="Сбор метаданных токенов")
    #
    # send_wallets_in_tg_task.apply_async(task_name="Отправка уведомлений в ТГ-канал с новыми Топ-кошельками")
