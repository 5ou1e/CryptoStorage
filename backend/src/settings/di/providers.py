from typing import AsyncGenerator, AsyncIterable

from dishka import Provider, Scope, provide
from fastapi_users.authentication import JWTStrategy
from fastapi_users.password import PasswordHelperProtocol
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.application.common.interfaces.readers import TokenReaderInterface, WalletReaderInterface
from src.application.common.interfaces.repositories import (
    SwapRepositoryInterface,
    TokenRepositoryInterface,
    UserRepositoryInterface,
    WalletRepositoryInterface,
    WalletTokenRepositoryInterface,
)
from src.application.common.interfaces.uow import UnitOfWorkInterface
from src.application.handlers.token.queries.get_token_by_address import GetTokenByAddressHandler
from src.application.handlers.token.queries.get_tokens import GetTokensHandler
from src.application.handlers.user.service import UserService
from src.application.handlers.wallet.commands.refresh_wallet_stats import RefreshWalletStatsCommandHandler
from src.application.handlers.wallet.queries.get_refresh_wallet_stats_status import GetRefreshWalletStatsStatusHandler
from src.application.handlers.wallet.queries.get_wallet_activities import GetWalletActivitiesHandler
from src.application.handlers.wallet.queries.get_wallet_by_address import GetWalletByAddressHandler
from src.application.handlers.wallet.queries.get_wallet_related_wallets import GetWalletRelatedWalletsHandler
from src.application.handlers.wallet.queries.get_wallet_tokens import GetWalletTokensHandler
from src.application.handlers.wallet.queries.get_wallets import GetWalletsHandler
from src.infra.db.sqlalchemy.readers import SQLAlchemyTokenReader, SQLAlchemyWalletReader
from src.infra.db.sqlalchemy.repositories import (
    SQLAlchemySwapRepository,
    SQLAlchemyTokenRepository,
    SQLAlchemyUserRepository,
    SQLAlchemyWalletRepository,
    SQLAlchemyWalletTokenRepository,
)
from src.infra.db.sqlalchemy.setup import AsyncSessionMaker
from src.infra.db.sqlalchemy.uow import SQLAlchemyUnitOfWork
from src.infra.db.tortoise.repositories import (
    TortoiseSwapRepository,
    TortoiseWalletRepository,
    TortoiseWalletTokenRepository,
)
from src.infra.providers.password_hasher_argon import ArgonPasswordHasher
from src.infra.redis.cache_service import RedisCacheService
from src.settings import config


class AppProvider(Provider):
    scope = Scope.REQUEST

    # Db
    @provide(scope=Scope.APP)
    def provide_sessionmaker(
        self,
    ) -> async_sessionmaker[AsyncSession]:
        return AsyncSessionMaker

    @provide(scope=Scope.REQUEST, provides=AsyncSession)
    async def provide_session(self, sessionmaker: async_sessionmaker[AsyncSession]) -> AsyncIterable[AsyncSession]:
        async with sessionmaker() as session:
            yield session

    uow = provide(SQLAlchemyUnitOfWork, provides=UnitOfWorkInterface)

    @provide(scope=Scope.APP)
    def get_redis(self) -> Redis:
        return Redis.from_url(config.redis.url, decode_responses=True)

    redis_cache_service = provide(RedisCacheService, scope=Scope.APP)

    # Auth
    @provide(scope=Scope.APP)
    def get_jwt_strategy(self) -> JWTStrategy:
        return JWTStrategy(
            secret=config.access_token.secret_key,
            lifetime_seconds=config.access_token.expire_minutes,
        )

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

    # Command Handlers
    refresh_wallet_stats_handler = provide(RefreshWalletStatsCommandHandler)
    get_refresh_wallet_stats_status_handler = provide(GetRefreshWalletStatsStatusHandler)


class GetWalletRelatedWalletsHandlerProvider(Provider):
    scope = Scope.REQUEST

    tortoise_swap_repository = provide(TortoiseSwapRepository, provides=SwapRepositoryInterface)
    tortoise_wallet_repository = provide(TortoiseWalletRepository, provides=WalletRepositoryInterface)
    tortoise_wallet_token_repository = provide(TortoiseWalletTokenRepository, provides=WalletTokenRepositoryInterface)

    get_wallet_related_wallets_handler = provide(GetWalletRelatedWalletsHandler)
