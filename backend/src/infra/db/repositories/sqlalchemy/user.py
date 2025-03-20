from typing import Any, Dict, Optional, Type

from sqlalchemy import func, select

from src.application.interfaces.repositories.user import BaseUserRepository
from src.domain.entities.user import UserEntity
from src.infra.db.models.sqlalchemy import User
from src.infra.db.models.sqlalchemy.common import Base
from src.infra.db.repositories.sqlalchemy.generic_repository import SQLAlchemyGenericRepository


class SQLAlchemyUserRepository(
    SQLAlchemyGenericRepository,
    BaseUserRepository,
):
    model_class = User
    entity_class = UserEntity
    oauth_account_model_class: Optional[Type[Base]]

    async def get_by_username(self, username: str) -> Optional[UserEntity]:
        stmt = select(self.model_class).where(self.model_class.username == username)
        result = await self._session.execute(stmt)
        return result.scalars().first()

    async def get_by_email(self, email: str) -> Optional[UserEntity]:
        stmt = select(self.model_class).where(func.lower(self.model_class.email) == email.lower())
        result = await self._session.execute(stmt)
        return result.scalars().first()

    async def get_by_oauth_account(self, oauth: str, account_id: str) -> Optional[UserEntity]:
        raise NotImplementedError

    async def add_oauth_account(
        self,
        user: UserEntity,
        create_dict: Dict[str, Any],
    ) -> UserEntity:
        raise NotImplementedError

    async def update_oauth_account(
        self,
        user: UserEntity,
        oauth_account: Base,
        update_dict: Dict[str, Any],
    ) -> UserEntity:
        raise NotImplementedError
