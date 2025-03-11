from dataclasses import dataclass

from src.application.exceptions import (
    ApplicationException,
)


@dataclass(eq=False)
class TokenNotFoundException(ApplicationException):
    address: str

    @property
    def title(self) -> str:
        return f'Токен с адресом "{self.address}" не найден'
