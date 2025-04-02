from typing import AsyncGenerator

from dishka import AsyncContainer, Provider, Scope, make_async_container, provide
from fastapi_users.password import PasswordHelperProtocol
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.interfaces.readers import TokenReaderInterface, WalletReaderInterface
from src.application.interfaces.repositories import (
    SwapRepositoryInterface,
    TokenRepositoryInterface,
    UserRepositoryInterface,
    WalletRepositoryInterface,
    WalletTokenRepositoryInterface,
)
from src.application.interfaces.uow import UnitOfWorkInterface
from src.application.token.queries.get_token_by_address import GetTokenByAddressHandler
from src.application.token.queries.get_tokens import GetTokensHandler
from src.application.user.service import UserService
from src.application.wallet.queries.get_wallet_activities import GetWalletActivitiesHandler
from src.application.wallet.queries.get_wallet_by_address import GetWalletByAddressHandler
from src.application.wallet.queries.get_wallet_related_wallets import GetWalletRelatedWalletsHandler
from src.application.wallet.queries.get_wallet_tokens import GetWalletTokensHandler
from src.application.wallet.queries.get_wallets import GetWalletsHandler
from src.infra.db.sqlalchemy.readers import SQLAlchemyTokenReader, SQLAlchemyWalletReader
from src.infra.db.sqlalchemy.repositories import (
    SQLAlchemySwapRepository,
    SQLAlchemyTokenRepository,
    SQLAlchemyUserRepository,
    SQLAlchemyWalletRepository,
    SQLAlchemyWalletTokenRepository,
)
from src.infra.db.sqlalchemy.setup import AsyncSessionLocal, get_db_session
from src.infra.db.sqlalchemy.uow import SQLAlchemyUnitOfWork
from src.infra.db.tortoise.repositories import (
    TortoiseSwapRepository,
    TortoiseWalletRepository,
    TortoiseWalletTokenRepository,
)
from src.infra.providers.password_hasher_argon import ArgonPasswordHasher


class AppProvider(Provider):
    scope = Scope.REQUEST

    async def get_db_session2(self) -> AsyncGenerator[AsyncSession, None]:
        # TODO : посмотреть почему прилетает аргумент с контейнером дишка
        async with AsyncSessionLocal() as session:
            yield session

    # Db
    db_session = provide(get_db_session2, provides=AsyncSession)
    uow = provide(SQLAlchemyUnitOfWork, provides=UnitOfWorkInterface)

    # Password-hasher
    password_hasher_argon = provide(ArgonPasswordHasher, provides=PasswordHelperProtocol)

    # Repositories
    user_repository = provide(SQLAlchemyUserRepository, provides=UserRepositoryInterface)
    wallet_repository = provide(SQLAlchemyWalletRepository, provides=WalletRepositoryInterface)
    token_repository = provide(SQLAlchemyTokenRepository, provides=TokenRepositoryInterface)
    wallet_token_repository = provide(SQLAlchemyWalletTokenRepository, provides=WalletTokenRepositoryInterface)
    swap_repository = provide(SQLAlchemySwapRepository, provides=SwapRepositoryInterface)

    # Readers
    wallet_reader = provide(SQLAlchemyWalletReader, provides=WalletReaderInterface)
    token_reader = provide(SQLAlchemyTokenReader, provides=TokenReaderInterface)

    # Services
    user_service = provide(UserService)

    # Query Handlers
    get_wallet_by_address_handler = provide(GetWalletByAddressHandler)
    get_wallets_handler = provide(GetWalletsHandler)
    get_wallet_tokens_handler = provide(GetWalletTokensHandler)
    get_wallet_activities_handler = provide(GetWalletActivitiesHandler)
    # get_wallet_related_wallets_handler = provide(GetWalletRelatedWalletsHandler)

    get_token_by_address_handler = provide(GetTokenByAddressHandler)
    get_tokens_handler = provide(GetTokensHandler)


class GetWalletRelatedWalletsHandlerProvider(Provider):
    scope = Scope.REQUEST

    async def get_db_session2(self) -> AsyncGenerator[AsyncSession, None]:
        async with AsyncSessionLocal() as session:
            yield session

    # Db
    db_session = provide(get_db_session2, provides=AsyncSession)
    uow = provide(SQLAlchemyUnitOfWork, provides=UnitOfWorkInterface)

    tortoise_swap_repository = provide(TortoiseSwapRepository, provides=SwapRepositoryInterface)
    tortoise_wallet_repository = provide(TortoiseWalletRepository, provides=WalletRepositoryInterface)
    tortoise_wallet_token_repository = provide(TortoiseWalletTokenRepository, provides=WalletTokenRepositoryInterface)

    get_wallet_related_wallets_handler = provide(GetWalletRelatedWalletsHandler)


def create_async_container() -> AsyncContainer:
    provider = AppProvider()
    get_wallet_related_wallets_handler_provider = GetWalletRelatedWalletsHandlerProvider()
    return make_async_container(provider, get_wallet_related_wallets_handler_provider)
