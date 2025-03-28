from abc import ABC, abstractmethod

from src.domain.entities.flipside import FlipsideAccount, FlipsideConfig

from .generic_repository import GenericRepositoryInterface


class FlipsideAccountRepositoryInterface(
    GenericRepositoryInterface[FlipsideAccount], ABC
):
    """Интерфейс репозитория FlipsdeAccount"""

    @abstractmethod
    async def get_first_active(self) -> FlipsideAccount:
        raise NotImplementedError

    @abstractmethod
    async def set_flipside_account_inactive(
        self,
        flipside_account: FlipsideAccount,
    ) -> None:
        raise NotImplementedError


class FlipsideConfigRepositoryInterface(
    GenericRepositoryInterface[FlipsideConfig], ABC
):
    """Интерфейс репозитория FlipsdeConfig"""

    @abstractmethod
    async def update_swaps_parsed_until_timestamp(self, entity: FlipsideConfig) -> None:
        raise NotImplementedError
