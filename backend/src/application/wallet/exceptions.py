from dataclasses import dataclass

from src.application.exceptions import ApplicationException


@dataclass(eq=False)
class WalletNotFoundException(ApplicationException):
    address: str

    @property
    def title(self) -> str:
        return f'Кошелек с адресом "{self.address}" не найден'


@dataclass(eq=False)
class RefreshWalletStatsTaskNotFoundException(ApplicationException):
    task_id: str

    @property
    def title(self) -> str:
        return f'Задача "{self.task_id}" не найдена'

