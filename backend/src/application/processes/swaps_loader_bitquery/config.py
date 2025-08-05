from datetime import datetime, timedelta

import pytz

from src.application.processes.swaps_loader.common import utils
from src.settings.config import config

EXTRACTOR_PARALLEL_WORKERS = config.swaps_loader.extractor_parallel_workers
EXTRACTOR_PERIOD_INTERVAL_MINUTES = config.swaps_loader.extractor_period_interval_minutes
PROCESS_INTERVAL_SECONDS = config.swaps_loader.process_interval_seconds
PERSISTENT_MODE = config.swaps_loader.persistent_mode
# Константы для фиксированного периода UTC
CONFIG_PERIOD_START_TIME = config.swaps_loader.config_period_start_time
CONFIG_PERIOD_END_TIME = config.swaps_loader.config_period_end_time


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
        raise ValueError("Не найден Flipside-конфиг в БД")

    last_tx_block_timestamp = flipside_config.swaps_parsed_until_block_timestamp
    if not last_tx_block_timestamp:
        raise ValueError("Не задано время в Flipside-конфиге")

    start_time = last_tx_block_timestamp.astimezone(pytz.UTC)
    end_time = (datetime.now(pytz.UTC) - timedelta(minutes=1440)).replace(second=0, microsecond=0)

    return start_time, end_time


def _get_period_from_config() -> tuple[datetime, datetime]:
    utc_tz = pytz.UTC
    start_time = utc_tz.localize(CONFIG_PERIOD_START_TIME)
    end_time = utc_tz.localize(CONFIG_PERIOD_END_TIME).replace(second=0, microsecond=0)
    return start_time, end_time


async def get_period_to_process() -> tuple[datetime, datetime]:
    if PERSISTENT_MODE:
        return await _get_period_from_db()
    return _get_period_from_config()
