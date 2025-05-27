from abc import ABC, abstractmethod
from typing import Any, Generic, Optional, TypeVar

from src.application.common.dto import Pagination
from src.domain.entities.base_entity import BaseEntity

Entity = TypeVar("Entity", bound=BaseEntity)


class GenericRepositoryInterface(Generic[Entity], ABC):
    """Интерфейс универсального репозитория"""

    @abstractmethod
    async def get_by_id(self, id_: Any) -> Entity | None:
        raise NotImplementedError

    @abstractmethod
    async def get_first(
        self,
        filters: Optional[dict] = None,
        sorting: Optional[list] = None,
        include: Optional[list] = None,
    ) -> list[Entity]:
        raise NotImplementedError

    @abstractmethod
    async def get_list(
        self,
        filters: Optional[dict] = None,
        sorting: Optional[list] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        include: Optional[list] = None,
    ) -> list[Entity]:
        raise NotImplementedError

    @abstractmethod
    async def create(self, entity: Entity) -> Entity:
        raise NotImplementedError

    @abstractmethod
    async def update(self, entity: Entity):
        raise NotImplementedError

    @abstractmethod
    async def delete(self, entity: Entity):
        raise NotImplementedError

    @abstractmethod
    async def delete_all(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def bulk_create(self, entities: list[Entity]) -> list[Entity]:
        raise NotImplementedError

    @abstractmethod
    async def bulk_update(self, entities: list[Entity]) -> list[Entity]:
        raise NotImplementedError
