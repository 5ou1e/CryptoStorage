from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.infra.db.repositories.sqlalchemy import (
    SQLAlchemySwapRepository,
    SQLAlchemyTokenRepository,
    SQLAlchemyUserRepository,
    SQLAlchemyWalletRepository,
    SQLAlchemyWalletTokenRepository,
)
from src.infra.db.repositories.tortoise import (
    TortoiseSwapRepository,
    TortoiseWalletRepository,
    TortoiseWalletTokenRepository,
)
from src.infra.db.setup import get_db_session


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
