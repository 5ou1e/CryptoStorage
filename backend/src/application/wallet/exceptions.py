from dataclasses import dataclass

from src.application.exceptions import ApplicationException


@dataclass(eq=False)
class WalletNotFoundException(ApplicationException):
    address: str

    @property
    def title(self) -> str:
        return f'Кошелек с адресом "{self.address}" не найден'
