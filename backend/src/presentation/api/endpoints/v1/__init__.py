from .auth import router as auth_router
from .test import router as test_router
from .token import router as token_router
from .wallet import router as wallet_router

__all__ = [
    "auth_router",
    "wallet_router",
    "token_router",
    "test_router",
]
