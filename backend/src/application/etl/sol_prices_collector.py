import asyncio
import logging
from datetime import datetime, timedelta

import pytz
import requests
from uuid6 import uuid7

from src.domain.constants import SOL_ADDRESS
from src.domain.entities.token import TokenPrice as TokenPrice
from src.infra.db.sqlalchemy.repositories import SQLAlchemyTokenPriceRepository, SQLAlchemyTokenRepository
from src.infra.db.sqlalchemy.setup import AsyncSessionLocal

logger = logging.getLogger("tasks.collect_sol_prices")


BINANCE_API_KLINES_URL = "https://api.binance.com/api/v3/klines"


async def collect_prices_async():
    token = await get_sol_token()
    if not token:
        raise ValueError("Токен WSOL не найден в БД!")
    start_time, end_time = await get_start_end_time(token)
    if not end_time > start_time:
        return
    symbol = "SOLUSDT"
    interval = "1m"
    current_time = start_time
    all_candles = []
    while current_time < end_time:
        next_time = min(current_time + timedelta(minutes=1000), end_time)  # Максимальный диапазон за запрос
        logger.info(f"Собираем цены с {current_time} до {next_time}...")
        try:
            candles = fetch_candles(
                symbol,
                interval,
                current_time,
                next_time,
            )
            all_candles.extend(candles)
            logger.debug(f"Собираем за период {current_time} - {next_time}")
        except Exception as e:
            logger.error(f"Ошибка при получении цен: {e}")
            raise e
        current_time = next_time
        await asyncio.sleep(0.1)  # Минимальная пауза для API Binance
    prices_to_load = await transform_data(all_candles, token)
    await load_prices_to_db(prices_to_load)
    logger.info(f"Цены успешно собраны за период с {start_time} до {end_time}!")


async def get_start_end_time(token):
    # Получаем последнюю запись из TokenPrice
    latest_token_price = await get_latest_token_price(token.id)
    utc_tz = pytz.timezone("UTC")
    if latest_token_price:
        start_time = latest_token_price.minute
    else:
        # Если нет записей, начинаем с какого-то фиксированного времени, например, с 1 сентября
        start_time = datetime(2024, 12, 1, 0, 0).astimezone(utc_tz)
    # Текущая минута
    end_time = datetime.now().astimezone(utc_tz)
    return start_time, end_time


def fetch_candles(symbol, interval, start_time, end_time):
    # Получение данных о свечах с ценами с Binance
    params = {
        "symbol": symbol,
        "interval": interval,
        "startTime": int(start_time.timestamp() * 1000),
        "endTime": int(end_time.timestamp() * 1000),
        "limit": 1000,  # Максимальное количество свечей за один запрос
    }
    response = requests.get(BINANCE_API_KLINES_URL, params=params, timeout=10)
    response.raise_for_status()
    return response.json()


async def transform_data(candles, token):
    result = []
    for candle in candles:
        timestamp = datetime.fromtimestamp((candle[0]) / 1000)  # Время закрытия свечи
        created_at = datetime.now()
        result.append(
            TokenPrice(
                id=uuid7(),
                token_id=token.id,
                minute=timestamp,
                price_usd=candle[4],
                created_at=created_at,
                updated_at=created_at,
            )
        )
    return result


async def get_sol_token():
    async with AsyncSessionLocal() as session:
        return await SQLAlchemyTokenRepository(session).get_by_address(
            address=SOL_ADDRESS,
        )


async def get_latest_token_price(token_id: str) -> TokenPrice | None:
    async with AsyncSessionLocal() as session:
        return await SQLAlchemyTokenPriceRepository(session).get_latest_by_token(token_id)


async def load_prices_to_db(prices: list[TokenPrice]):
    async with AsyncSessionLocal() as session:
        await SQLAlchemyTokenPriceRepository(session).bulk_create(
            prices,
            ignore_conflicts=True,
        )
        await session.commit()
