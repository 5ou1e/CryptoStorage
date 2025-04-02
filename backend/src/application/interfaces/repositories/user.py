from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from tortoise.models import Model

from src.application.interfaces.repositories.generic_repository import (
    GenericRepositoryInterface,
)
from src.domain.entities.user import User


class UserRepositoryInterface(GenericRepositoryInterface[User], ABC):

    @abstractmethod
    async def get_by_username(self, username: str) -> Optional[User]:
        raise NotImplementedError

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        raise NotImplementedError

    @abstractmethod
    async def get_by_oauth_account(self, oauth: str, account_id: str) -> Optional[User]:
        raise NotImplementedError

    @abstractmethod
    async def add_oauth_account(
        self,
        user: User,
        create_dict: Dict[str, Any],
    ) -> User:
        raise NotImplementedError

    @abstractmethod
    async def update_oauth_account(
        self,
        user: User,
        oauth_account: Model,
        update_dict: Dict[str, Any],
    ) -> User:
        raise NotImplementedError
