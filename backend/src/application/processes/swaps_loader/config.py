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
    "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
    "JUPyiwrYJFskUPiHa7hkeR8VUtAeFoSYbKedZNsDvCN",
    "pumpCmXqMfrsAkQ5r49WcJnRayYRqmXz6ae8H7H9Dfn",
    "2zMMhcVQEXDtdE6vsFS7S7D5oUodfJHE8vd1gnBouauv",
    "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB",
    "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263",
    "27G8MtK7VtTcCHkpASjSDdkWWYfoqT6ggEuKidVJidD4",
    "jtojtomepa8beP8AuQc6eXt5FriJwfFMwQx2v2f9mCL",
    "rndrizKT3MK1iimdxRdWabcF7Zg7AR5T4nud4EkHBof",
    "HZ1JovNiVvGrGNiiYvEozEVgZ58xaU3RKwX8eACQBCt3",
    "4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R",
    "jupSoLaHXQiZZTSfEWMTRRgpnyFm8f6sZdosWBjx93v",
    "85VBFQZC9TZkfaptBWjvUw7YbZjy52A6mjtPGjstQAmQ",
    "MEFNBXixkEbait3xn9bkm8WsJzXtVsaJEn4c8Sam21u",
    "Grass7B4RdKfBCjTKgSqnXkqjwiGvQyFbuSCUJr3XXjs",
    "LAYER4xPpTCb3QL8S9u41EAhAX7mhBn8Q6xMTwY2Yzc",
    "ZBCNpuD7YMXzTHB2fhGkGi78MNsHGLRXUhRewNRm9RU",
    "DriFtupJYLTosbwoN8koMbEYSx54aFAVLddWsbksjwg7",
    "KMNo3nJsBXfcpJTVhZcXLW7RmTwTt4GVFE7suUBo9sS",
    "cbbtcf3aa214zXHbiAZQwf4122FBYbraNdFqgw4iMij",
    "2FPyTwcZLUg1MDrwsyoP4D6s1tM7hAkHYRjkNb5w6Pxk",
    "3NZ9JMVBmGAqocybic2c7LQCJScmgsAZ6vQqTDzcqmJh",
    "4Z8wM5BEVD5RHZ79AJ5XUN23tsEWSGZne2qqNm647Q9o",
    "Bybit2vBJGhPF52GBdNaQfUJ6ZpThSgHBobjWZpLPb4B",
    "HUMA1821qVDKta3u2ovmfDQeW2fSQouSKE8fkF44wvGw",
    "Dso1bDeDjCQxTrWHqUUi63oBvV7Mdm6WaobLbQ7gnPQ",
    "vSoLxydx6akxyMD9XEcPvGYNGq6Nn66oqVb3UkGkei7",
    "z3dn17yLaGMKffVogeFHQ9zWVcXgqgf3PQnDsNs2g6M",
    "7vfCXTUXx5WJV5JADk17DUJ4ksgau7utNKj4b963voxs",
    "A1KLoBrKBde8Ty9qtNQUtq3C2ortoC3u7twggz7sEto6",
    "TNSRxcUxoT9xBG3de7PiJyTDYu7kskLqcpddxnEJAS6",
    "sSo14endRuUbvQaJS3dq36Q829a3A6BEfoeeRGJywEh",
    "HzwqbKZw8HxMN6bF2yFZNrht3c2iXXzpKcFu7uBEDKtr",
    "AvZZF1YaZDziPY2RCK4oJrRVrbN3mTD9NL24hPeaZeUj",
    "picobAEvs6w7QEknPce34wAE4gknZA9v5tTonnmHYdX",
    "BonK1YhkXEGLZzwtcvRTip3gAL9nCeQD7ppZBLXhtTs",
    "9n4nbM75f5Ui33ZbPYXn59EwSgE8CGsHtAeTH5YFeJ9E",
    "LSTxxxnJzKDFSLr4dUkPcmCf5VyryEqzPLz5j4bpxFp",
    "bgSoLfRx1wRPehwC9TyG568AGjnf1sQG1MYa8s3FbfY",
    "bSo13r4TkiE4KumL71LsHTPpL2euBYLFx6h9HP3piy1",
    "5oVNBeEEQvYi1cX3ir8Dx5n1P7pdxydbGF2X4TxVusJm",
    "mSoLzYCxHdYgdzU16g5QSh3i5K3z3KZK7ytfqcJm7So",
    "J1toso1uCk3RLmjorhTtrVwY9HJ7X8V9yYac6Y7kGCPn",
    "BZLbGTNCSFfoth2GYDtwr7e4imWzpR5jqcUuGEwr646K",
    "BNso1VUJnh4zcfpZa6986Ea66P6TCp59hvtNJ8b1X85",
    "7i5KKsX2weiTkry7jA4ZwSuXGhs5eJBEjY8vVxR4pfRx",
    "METAewgxyPbgwsseH8T16a39CQ5VyVxZi9zXiDPY18m",
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
