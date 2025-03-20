from datetime import datetime

from sqlalchemy import select

from src.domain.constants import SOL_ADDRESS
from src.infra.db.models.sqlalchemy import (
    Token,
    TokenPrice,
)
from src.infra.db.repositories.sqlalchemy.flipside import (
    SQLAlchemyFlipsideAccountRepository,
    SQLAlchemyFlipsideConfigRepository,
)
from src.infra.db.setup import AsyncSessionLocal


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


async def get_flipside_account():
    async with AsyncSessionLocal() as session:
        repo = SQLAlchemyFlipsideAccountRepository(session)
        return await repo.get_flipside_account()


async def get_flipside_config():
    async with AsyncSessionLocal() as session:
        repo = SQLAlchemyFlipsideConfigRepository(session)
        return await repo.get_flipside_config()


async def set_flipside_account_inactive(
    flipside_account,
):
    async with AsyncSessionLocal() as session:
        repo = SQLAlchemyFlipsideAccountRepository(session)
        await repo.set_flipside_account_inactive(flipside_account)
        await session.commit()


async def get_sol_prices(
    minute_from: datetime,
    minute_to: datetime,
):
    # TODO переместить в репозиторий
    async with AsyncSessionLocal() as session:
        stmt = select(Token).where(Token.address == SOL_ADDRESS).limit(1)
        result = await session.execute(stmt)
        sol_token = result.scalars().first()
        if not sol_token:
            raise ValueError(f"Токен WSOL не найден в БД!")
        stmt = select(TokenPrice).where(
            TokenPrice.token == sol_token, TokenPrice.minute >= minute_from, TokenPrice.minute <= minute_to
        )

        result = await session.execute(stmt)
        _sol_prices = result.scalars().all()
        sol_prices = {price.minute: price.price_usd for price in _sol_prices}
        return sol_prices
