from dishka import AsyncContainer, make_async_container
from src.settings.ioc.providers import AppProvider, GetWalletRelatedWalletsHandlerProvider


def create_async_container() -> AsyncContainer:
    provider = AppProvider()
    get_wallet_related_wallets_handler_provider = GetWalletRelatedWalletsHandlerProvider()
    return make_async_container(provider, get_wallet_related_wallets_handler_provider)
