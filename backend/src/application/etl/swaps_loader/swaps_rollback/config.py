from datetime import datetime, timedelta

import pytz

from src.application.etl.swaps_loader.common import utils

EXTRACTOR_PARALLEL_WORKERS = 1
EXTRACTOR_PERIOD_INTERVAL_MINUTES = 1
PROCESS_INTERVAL_SECONDS = 3600  # Интервал запуска процесса для PERSISTENT_MODE в секундах
PERSISTENT_MODE = False  # Переключатель: True — постоянный процесс, False — использовать фиксированный период
# Константы для фиксированного периода UTC
CONFIG_PERIOD_START_TIME = (2025, 1, 18, 19, 0, 0)
CONFIG_PERIOD_END_TIME = (2025, 1, 18, 19, 1, 0)

BLACKLISTED_TOKENS = {
    "JUPyiwrYJFskUPiHa7hkeR8VUtAeFoSYbKedZNsDvCN",
    "HZ1JovNiVvGrGNiiYvEozEVgZ58xaU3RKwX8eACQBCt3",
    "rndrizKT3MK1iimdxRdWabcF7Zg7AR5T4nud4EkHBof",
    "85VBFQZC9TZkfaptBWjvUw7YbZjy52A6mjtPGjstQAmQ",
    "jtojtomepa8beP8AuQc6eXt5FriJwfFMwQx2v2f9mCL",
    "BZLbGTNCSFfoth2GYDtwr7e4imWzpR5jqcUuGEwr646K",
    "Grass7B4RdKfBCjTKgSqnXkqjwiGvQyFbuSCUJr3XXjs",
    "4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R",
    "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263",
    "KMNo3nJsBXfcpJTVhZcXLW7RmTwTt4GVFE7suUBo9sS",
    "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB",
    "DriFtupJYLTosbwoN8koMbEYSx54aFAVLddWsbksjwg7",
    "27G8MtK7VtTcCHkpASjSDdkWWYfoqT6ggEuKidVJidD4",
    "BNso1VUJnh4zcfpZa6986Ea66P6TCp59hvtNJ8b1X85",
    "jupSoLaHXQiZZTSfEWMTRRgpnyFm8f6sZdosWBjx93v",
    "TNSRxcUxoT9xBG3de7PiJyTDYu7kskLqcpddxnEJAS6",
    "7i5KKsX2weiTkry7jA4ZwSuXGhs5eJBEjY8vVxR4pfRx",
    "z3dn17yLaGMKffVogeFHQ9zWVcXgqgf3PQnDsNs2g6M",
    "METAewgxyPbgwsseH8T16a39CQ5VyVxZi9zXiDPY18m",
    "3NZ9JMVBmGAqocybic2c7LQCJScmgsAZ6vQqTDzcqmJh",
    "7vfCXTUXx5WJV5JADk17DUJ4ksgau7utNKj4b963voxs",
    "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
}


async def _get_period_from_db() -> tuple[datetime, datetime]:
    flipside_config = await utils.get_flipside_config()
    if not flipside_config:
        raise ValueError("Не найден FlipsideCrypto-конфиг в БД")

    last_tx_block_timestamp = flipside_config.swaps_parsed_until_block_timestamp
    if not last_tx_block_timestamp:
        raise ValueError("Ошибка - не задано время в flipsidecrypto-config'e")

    start_time = last_tx_block_timestamp.astimezone(pytz.UTC)
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
