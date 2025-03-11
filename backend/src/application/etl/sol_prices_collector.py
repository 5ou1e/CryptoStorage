import asyncio
import logging
from datetime import datetime, timedelta

import pytz
import requests
from tortoise import Tortoise

from src.infra.db.models.tortoise import (
    Token,
    TokenPrice,
)
from src.infra.db.setup_tortoise import (
    init_db_async,
)
from src.settings import config

logger = logging.getLogger("tasks.collect_sol_prices")


async def collect_prices_async():
    await init_db_async()
    token = await Token.filter(address=config.solana.token_address).first()
    if not token:
        raise ValueError("Токен SOL отсутствует в БД!")
    start_time, end_time = await get_start_end_time()
    if not end_time > start_time:
        return
    symbol = "SOLUSDT"
    interval = "1m"
    current_time = start_time
    all_candles = []
    while current_time < end_time:
        next_time = current_time + timedelta(minutes=1000)  # Максимальный диапазон за запрос
        if next_time > end_time:
            next_time = end_time
        logger.info(f"Собираем цены с  {current_time} до {next_time}...")
        try:
            candles = fetch_candles(
                symbol,
                interval,
                current_time,
                next_time,
            )
            all_candles.extend(candles)
            logger.debug(current_time, next_time)
        except Exception as e:
            logger.error(f"Ошибка при получении цен: {e}")
            raise e
        current_time = next_time
        await asyncio.sleep(0.1)  # Минимальная пауза для API Binance
    await import_prices_to_db(all_candles, token)
    logger.info("Цены собраны!")
    await Tortoise.close_connections()


async def get_start_end_time():
    # Получаем последнюю запись из TokenPrice
    last_token_price = (
        await TokenPrice.filter(
            token__address=config.solana.token_address,
        )
        .order_by("-minute")
        .first()
    )
    utc_tz = pytz.timezone("UTC")
    if last_token_price:
        start_time = last_token_price.minute
    else:
        # Если нет записей, начинаем с какого-то фиксированного времени, например, с 1 сентября
        start_time = datetime(2024, 12, 1, 0, 0).astimezone(utc_tz)
    # Текущая минута
    end_time = datetime.now().astimezone(utc_tz)
    return start_time, end_time


def fetch_candles(symbol, interval, start_time, end_time):
    # Получение данных о свечах с ценами с Binance
    url = "https://api.binance.com/api/v3/klines"
    params = {
        "symbol": symbol,
        "interval": interval,
        "startTime": int(start_time.timestamp() * 1000),
        "endTime": int(end_time.timestamp() * 1000),
        "limit": 1000,  # Максимальное количество свечей за один запрос
    }
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    return response.json()


async def import_prices_to_db(candles, token):
    objects_to_create = []
    for candle in candles:
        timestamp = datetime.fromtimestamp((candle[0]) / 1000)  # Время закрытия свечи
        objects_to_create.append(
            TokenPrice(
                token=token,
                minute=timestamp,
                price_usd=candle[4],
            )
        )
    await TokenPrice.bulk_create(
        objects_to_create,
        ignore_conflicts=True,
    )
