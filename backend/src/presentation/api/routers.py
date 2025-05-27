from fastapi import APIRouter

from src.presentation.api.endpoints.auth import router as auth_router
from src.presentation.api.endpoints.default import docs_router, root_router
from src.presentation.api.endpoints.v1 import token_router, wallet_router
from src.settings import config


def create_v1_router():
    """Подключение роутеров."""
    v1_router = APIRouter(prefix=config.api.v1.prefix)
    v1_router_list = [
        wallet_router,
        token_router,
    ]
    for router in v1_router_list:
        v1_router.include_router(router)

    return v1_router


def setup_routers(app) -> None:
    """Подключение роутеров."""
    v1_router = create_v1_router()

    api_router = APIRouter(prefix=config.api.prefix)

    api_router.include_router(docs_router)
    api_router.include_router(auth_router)
    api_router.include_router(v1_router)

    app.include_router(root_router)
    app.include_router(api_router)
