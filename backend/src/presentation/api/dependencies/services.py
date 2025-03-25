from typing import Annotated

from fastapi import Depends

from src.application.token.queries.get_token_by_address import GetTokenByAddressHandler
from src.application.token.queries.get_tokens import GetTokensHandler
from src.application.user.service import UserService
from src.application.wallet.queries.get_wallet_activities import GetWalletActivitiesHandler
from src.application.wallet.queries.get_wallet_by_address import GetWalletByAddressHandler
from src.application.wallet.queries.get_wallet_related_wallets import GetWalletRelatedWalletsHandler
from src.application.wallet.queries.get_wallet_tokens import GetWalletTokensHandler
from src.application.wallet.queries.get_wallets import GetWalletsHandler
from src.infra.db.sqlalchemy.setup import get_db_session
from src.infra.db.sqlalchemy.uow import SQLAlchemyUnitOfWork
from src.infra.processors.password_hasher_argon import password_hasher_argon

from .repositories import (
    get_swap_repository,
    get_swap_repository_tortoise,
    get_token_reader,
    get_token_repository,
    get_user_repository,
    get_wallet_reader,
    get_wallet_repository,
    get_wallet_repository_tortoise,
    get_wallet_token_repository,
    get_wallet_token_repository_tortoise,
)


def get_uow(session=Depends(get_db_session)):
    return SQLAlchemyUnitOfWork(session)


def get_user_service(
    uow=Depends(get_uow),
    user_repository=Depends(get_user_repository),
):
    return UserService(uow, user_repository, password_hasher_argon)


def get_wallet_by_address_handler(
    reader=Depends(get_wallet_reader),
):
    return GetWalletByAddressHandler(reader)


GetWalletByAddressHandlerDep = Annotated[
    GetWalletByAddressHandler,
    Depends(get_wallet_by_address_handler),
]


def get_wallets_handler(
    reader=Depends(get_wallet_reader),
):
    return GetWalletsHandler(reader)


GetWalletsHandlerDep = Annotated[
    GetWalletsHandler,
    Depends(get_wallets_handler),
]


def get_wallet_tokens_handler(
    reader=Depends(get_wallet_reader),
):
    return GetWalletTokensHandler(reader)


GetWalletTokensHandlerDep = Annotated[
    GetWalletTokensHandler,
    Depends(get_wallet_tokens_handler),
]


def get_wallet_activities_handler(reader=Depends(get_wallet_reader)):
    return GetWalletActivitiesHandler(reader)


GetWalletActivitiesHandlerDep = Annotated[
    GetWalletActivitiesHandler,
    Depends(get_wallet_activities_handler),
]


def get_wallet_related_wallets_handler(
    wallet_repository=Depends(get_wallet_repository_tortoise),
    wallet_token_repository=Depends(get_wallet_token_repository_tortoise),
    swap_repository=Depends(get_swap_repository_tortoise),
):
    return GetWalletRelatedWalletsHandler(
        wallet_repository,
        wallet_token_repository,
        swap_repository,
    )


GetWalletRelatedWalletsHandlerDep = Annotated[
    GetWalletRelatedWalletsHandler,
    Depends(get_wallet_related_wallets_handler),
]


def get_token_by_address_handler(
    token_reader=Depends(get_token_reader),
):
    return GetTokenByAddressHandler(token_reader)


GetTokenByAddressHandlerDep = Annotated[
    GetTokenByAddressHandler,
    Depends(get_token_by_address_handler),
]


def get_tokens_handler(
    token_reader=Depends(get_token_reader),
):
    return GetTokensHandler(token_reader)


GetTokensHandlerDep = Annotated[GetTokensHandler, Depends(get_tokens_handler)]
