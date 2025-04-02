from fastapi import APIRouter

from src.presentation.api.endpoints.common import docs_router, root_router
from src.presentation.api.endpoints.v1 import (
    auth_router,
    test_router,
    token_router,
    wallet_router,
)
from src.settings import config


def setup_routers(app) -> None:
    """Подключение роутеров."""
    v1_router = APIRouter(prefix=config.api.v1.prefix)
    v1_router_list = [
        test_router,
        auth_router,
        wallet_router,
        token_router,
    ]
    for router in v1_router_list:
        v1_router.include_router(router)
    api_router = APIRouter(prefix=config.api.prefix)
    api_router.include_router(v1_router)
    api_router.include_router(docs_router)
    app.include_router(root_router)
    app.include_router(api_router)
