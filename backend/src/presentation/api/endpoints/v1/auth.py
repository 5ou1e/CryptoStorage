from fastapi import APIRouter

from src.application.user.dto import (
    UserCreateDTO,
    UserReadDTO,
)
from src.presentation.api.dependencies.auth import (
    auth_backend,
    fastapi_users,
)

router = APIRouter(
    prefix="/auth",
    tags=["Auth&Пользователи"],
)

# Эндпоинты авторизации
router.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/jwt",
)

# Эндпоинты регистрации
router.include_router(
    fastapi_users.get_register_router(UserReadDTO, UserCreateDTO),
    prefix="",
)
