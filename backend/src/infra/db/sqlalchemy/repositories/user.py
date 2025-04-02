from typing import Any, Dict, Optional, Type

from sqlalchemy import func, select

from src.application.interfaces.repositories.user import UserRepositoryInterface
from src.domain.entities.user import User as UserEntity
from src.infra.db.sqlalchemy.models import User
from src.infra.db.sqlalchemy.models.common import Base
from src.infra.db.sqlalchemy.repositories.generic_repository import (
    SQLAlchemyGenericRepository,
)


class SQLAlchemyUserRepository(
    SQLAlchemyGenericRepository,
    UserRepositoryInterface,
):
    model_class = User
    entity_class = UserEntity
    oauth_account_model_class: Optional[Type[Base]]

    async def get_by_username(self, username: str) -> Optional[UserEntity]:
        stmt = select(self.model_class).where(self.model_class.username == username)
        result = await self._session.execute(stmt)
        instance = result.scalars().first()
        return self.model_to_entity(instance) if instance else None

    async def get_by_email(self, email: str) -> Optional[UserEntity]:
        stmt = select(self.model_class).where(func.lower(self.model_class.email) == email.lower())
        result = await self._session.execute(stmt)
        instance = result.scalars().first()
        entity = self.model_to_entity(instance) if instance else None
        return entity

    async def get_by_oauth_account(self, oauth: str, account_id: str) -> Optional[UserEntity]:
        raise NotImplementedError

    async def add_oauth_account(
        self,
        user: User,
        create_dict: Dict[str, Any],
    ) -> UserEntity:
        raise NotImplementedError

    async def update_oauth_account(
        self,
        user: User,
        oauth_account: Base,
        update_dict: Dict[str, Any],
    ) -> UserEntity:
        raise NotImplementedError
