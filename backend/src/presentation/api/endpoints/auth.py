from fastapi import APIRouter

from src.application.handlers.user.dto import UserCreateDTO, UserReadDTO
from src.presentation.api.dependencies.auth import auth_backend, fastapi_users

router = APIRouter(
    prefix="/auth",
    tags=["Auth&Пользователи"],
)

# Эндпоинты login / logout
router.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/jwt",
)

# Эндпоинты register
router.include_router(
    fastapi_users.get_register_router(UserReadDTO, UserCreateDTO),
    prefix="",
)
