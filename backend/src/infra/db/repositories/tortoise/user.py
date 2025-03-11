from typing import (
    Any,
    Dict,
    Optional,
    Type,
    TypeVar,
)

from tortoise.expressions import F, Q
from tortoise.models import Model

from src.application.interfaces.repositories.user import (
    BaseUserRepository,
)
from src.domain.entities.user import UserEntity
from src.infra.db.models.tortoise import User
from src.infra.db.repositories.tortoise.generic_repository import (
    TortoiseGenericRepository,
)

ID = TypeVar("ID", bound=Any)


class TortoiseUserRepository(TortoiseGenericRepository, BaseUserRepository):
    """
    Database adapter for Tortoise ORM.

    :param model_class: Tortoise ORM user model.
    :param oauth_account_model: Optional Tortoise ORM OAuth accounts model.
    """

    model_class = User
    entity_class = UserEntity
    oauth_account_model_class: Optional[Type[Model]]

    async def get_by_username(self, username: str) -> Optional[UserEntity]:
        return await self.model_class.get(username=username)

    async def get_by_email(self, email: str) -> Optional[UserEntity]:
        from tortoise import functions

        condition = Q(email=functions.Lower(F("email"))) & Q(email__iexact=email.lower())
        return await self.model_class.filter(condition).first()

    async def get_by_oauth_account(self, oauth: str, account_id: str) -> Optional[UserEntity]:
        if self.oauth_account_model is None:
            raise NotImplementedError

        return await self.model_class.filter(
            oauth_account__oauth_name=oauth,
            oauth_account__account_id=account_id,
        ).first()

    async def add_oauth_account(
        self,
        user: UserEntity,
        create_dict: Dict[str, Any],
    ) -> UserEntity:
        if self.oauth_account_model_class is None:
            raise NotImplementedError
        oauth_account = await self.oauth_account_model_class.create(**create_dict)
        user.oauth_accounts.add(oauth_account)  # Связь через ManyToMany или ForeignKey
        await user.save()

        return user

    async def update_oauth_account(
        self,
        user: UserEntity,
        oauth_account: Model,
        update_dict: Dict[str, Any],
    ) -> UserEntity:
        for key, value in update_dict.items():
            setattr(oauth_account, key, value)

        await oauth_account.save()
        return user
