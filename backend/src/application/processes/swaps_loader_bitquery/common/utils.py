from datetime import datetime

from src.domain.constants import SOL_ADDRESS
from src.domain.entities import FlipsideAccount, FlipsideConfig
from src.infra.db.sqlalchemy.repositories import SQLAlchemyTokenPriceRepository, SQLAlchemyTokenRepository
from src.infra.db.sqlalchemy.repositories.flipside import (
    SQLAlchemyFlipsideAccountRepositoryInterface,
    SQLAlchemyFlipsideConfigRepositoryInterface,
)
from src.infra.db.sqlalchemy.setup import AsyncSessionMaker


def split_time_range(start_time, end_time, parts):
    """Разбивает временной промежуток на равные части"""
    delta = (end_time - start_time) / parts
    intervals = [
        (
            start_time + i * delta,
            start_time + (i + 1) * delta,
        )
        for i in range(parts - 1)
    ]
    # Добавляем последний интервал, чтобы гарантировать точное совпадение с end_time
    intervals.append(
        (
            start_time + (parts - 1) * delta,
            end_time,
        )
    )
    return intervals


async def get_flipside_account() -> FlipsideAccount:
    async with AsyncSessionMaker() as session:
        repo = SQLAlchemyFlipsideAccountRepositoryInterface(session)
        return await repo.get_first_active()


async def get_flipside_config() -> FlipsideConfig:
    async with AsyncSessionMaker() as session:
        repo = SQLAlchemyFlipsideConfigRepositoryInterface(session)
        return await repo.get_first()


async def set_flipside_account_inactive(
    flipside_account,
):
    async with AsyncSessionMaker() as session:
        repo = SQLAlchemyFlipsideAccountRepositoryInterface(session)
        await repo.set_flipside_account_inactive(flipside_account)
        await session.commit()


async def get_sol_prices(
    minute_from: datetime,
    minute_to: datetime,
):
    async with AsyncSessionMaker() as session:
        sol_token = await SQLAlchemyTokenRepository(session).get_by_address(SOL_ADDRESS)
        if not sol_token:
            raise ValueError(f"Токен WSOL не найден в БД!")
        prices = await SQLAlchemyTokenPriceRepository(session).get_prices_by_token(
            sol_token.id, minute_from=minute_from, minute_to=minute_to
        )
        prices_dict = {price.minute: price.price_usd for price in prices}
        return prices_dict


def is_base_address(address: str) -> bool:
    """Проверяет является ли адрес токена базовым - SOL/WSOL"""

    base_addresses = {
        "11111111111111111111111111111111",  # SOL (hex/shortened)
        "So11111111111111111111111111111111111111111",  # SOL
        "So11111111111111111111111111111111111111112"  # WSOL
    }

    return address in base_addresses
