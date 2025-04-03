from typing import Annotated
from uuid import UUID

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import Depends
from fastapi_users import FastAPIUsers
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)

from src.application.user.service import UserService
from src.domain.entities.user import User

bearer_transport = BearerTransport(tokenUrl="v1/auth/jwt/login")


@inject
async def get_jwt_strategy(jwt_strategy: FromDishka[JWTStrategy]):
    return jwt_strategy


@inject
def get_user_service(service: FromDishka[UserService]):
    return service


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
