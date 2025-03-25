from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.infra.db.sqlalchemy.readers import SQLAlchemyTokenReader, SQLAlchemyWalletReader
from src.infra.db.sqlalchemy.repositories import (
    SQLAlchemySwapRepository,
    SQLAlchemyTokenRepository,
    SQLAlchemyUserRepository,
    SQLAlchemyWalletRepository,
    SQLAlchemyWalletTokenRepository,
)
from src.infra.db.sqlalchemy.setup import get_db_session
from src.infra.db.tortoise.repositories import (
    TortoiseSwapRepository,
    TortoiseWalletRepository,
    TortoiseWalletTokenRepository,
)


async def get_wallet_reader(
    session: AsyncSession = Depends(get_db_session),
):
    return SQLAlchemyWalletReader(session)


async def get_token_reader(
    session: AsyncSession = Depends(get_db_session),
):
    return SQLAlchemyTokenReader(session)


def get_user_repository(
    session: AsyncSession = Depends(get_db_session),
):
    return SQLAlchemyUserRepository(session)


def get_wallet_repository(
    session: AsyncSession = Depends(get_db_session),
):
    return SQLAlchemyWalletRepository(session)


def get_token_repository(
    session: AsyncSession = Depends(get_db_session),
):
    return SQLAlchemyTokenRepository(session)


def get_wallet_token_repository(
    session: AsyncSession = Depends(get_db_session),
):
    return SQLAlchemyWalletTokenRepository(session)


def get_swap_repository(
    session: AsyncSession = Depends(get_db_session),
):
    return SQLAlchemySwapRepository(session)


def get_wallet_repository_tortoise():
    return TortoiseWalletRepository()


def get_wallet_token_repository_tortoise():
    return TortoiseWalletTokenRepository()


def get_swap_repository_tortoise():
    return TortoiseSwapRepository()
