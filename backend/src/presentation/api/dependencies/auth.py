from typing import Annotated
from uuid import UUID

from fastapi import Depends
from fastapi_users import FastAPIUsers
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)
from src.domain.entities.user import User
from src.infra.db.tortoise.models import User
from src.presentation.api.dependencies.services import get_user_service
from src.settings import config

bearer_transport = BearerTransport(tokenUrl="v1/auth/jwt/login")


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(
        secret=config.access_token.secret_key,
        lifetime_seconds=config.access_token.expire_minutes,
    )


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)


fastapi_users = FastAPIUsers[User, UUID](
    get_user_service,
    [auth_backend],
)


get_current_user = fastapi_users.current_user()
CurrentUserDep = Annotated[User, Depends(get_current_user)]
