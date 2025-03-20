from abc import ABC

from src.domain.entities.flipside import FlipsideAccountEntity, FlipsideConfigEntity

from .generic_repository import BaseGenericRepository


class BaseFlipsideAccountRepository(BaseGenericRepository[FlipsideAccountEntity], ABC):
    """Интерфейс репозитория FlipsdeAccount"""

    pass


class BaseFlipsideConfigRepository(BaseGenericRepository[FlipsideConfigEntity], ABC):
    """Интерфейс репозитория FlipsdeConfig"""

    pass
