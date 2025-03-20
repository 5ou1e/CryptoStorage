from datetime import datetime, timedelta

import pytz

from src.application.etl.swaps_loader.common import utils

EXTRACTOR_PARALLEL_WORKERS = 6
EXTRACTOR_PERIOD_INTERVAL_MINUTES = 30
PROCESS_INTERVAL_SECONDS = 3600  # Интервал запуска процесса для PERSISTENT_MODE в секундах
PERSISTENT_MODE = False  # Переключатель: True — постоянный процесс, False — использовать фиксированный период
# Константы для фиксированного периода UTC
CONFIG_PERIOD_START_TIME = (2025, 1, 12, 7, 0, 0)
CONFIG_PERIOD_END_TIME = (2025, 3, 1, 20, 20, 0)


async def _get_period_from_db() -> tuple[datetime, datetime]:
    flipside_config = await utils.get_flipside_config()
    if not flipside_config:
        return ValueError("Не найден FlipsideCrypto-конфиг в БД")

    last_tx_inserted_timestamp = flipside_config.swaps_parsed_untill_inserted_timestamp
    if not last_tx_inserted_timestamp:
        raise ValueError("Ошибка - не задано время в flipsidecrypto-config'e")

    start_time = last_tx_inserted_timestamp.astimezone(pytz.UTC)
    end_time = (datetime.now(pytz.UTC) - timedelta(minutes=1440)).replace(second=0, microsecond=0)

    return start_time, end_time


def _get_period_from_config() -> tuple[datetime, datetime]:
    utc_tz = pytz.UTC
    start_time = utc_tz.localize(datetime(*CONFIG_PERIOD_START_TIME))
    end_time = utc_tz.localize(datetime(*CONFIG_PERIOD_END_TIME)).replace(second=0, microsecond=0)
    return start_time, end_time


async def get_period_to_process() -> tuple[datetime, datetime]:
    if PERSISTENT_MODE:
        return await _get_period_from_db()
    return _get_period_from_config()
