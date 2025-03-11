from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from tortoise.models import Model

from src.application.interfaces.repositories.generic_repository import (
    BaseGenericRepository,
)
from src.domain.entities.user import UserEntity


class BaseUserRepository(BaseGenericRepository[UserEntity], ABC):

    @abstractmethod
    async def get_by_username(self, username: str) -> Optional[UserEntity]:
        raise NotImplementedError

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[UserEntity]:
        raise NotImplementedError

    @abstractmethod
    async def get_by_oauth_account(self, oauth: str, account_id: str) -> Optional[UserEntity]:
        raise NotImplementedError

    @abstractmethod
    async def add_oauth_account(
        self,
        user: UserEntity,
        create_dict: Dict[str, Any],
    ) -> UserEntity:
        raise NotImplementedError

    @abstractmethod
    async def update_oauth_account(
        self,
        user: UserEntity,
        oauth_account: Model,
        update_dict: Dict[str, Any],
    ) -> UserEntity:
        raise NotImplementedError
