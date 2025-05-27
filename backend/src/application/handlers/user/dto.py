from uuid import UUID

from fastapi_users import schemas
from pydantic import BaseModel, Field, model_validator


class UserReadDTO(schemas.BaseUser[UUID]):
    username: str | None = Field(None, max_length=150)


class UserCreateDTO(schemas.BaseUserCreate):
    username: str | None = Field(None, max_length=150)

    @model_validator(mode="before")
    def set_username(cls, data):
        # Устанавливаем email в username, если не передан
        if "username" not in data or not data["username"]:
            data["username"] = data["email"]
        return data


class UserUpdateDTO(UserReadDTO):
    pass


class UserDTO(BaseModel):
    username: str | None = Field(None, max_length=150)

    class Config:
        from_attributes = True


class UsersDTO(BaseModel):
    users: list[UserDTO]
