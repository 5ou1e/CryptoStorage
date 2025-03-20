from dataclasses import dataclass

from src.application.exceptions import ApplicationException


@dataclass(eq=False)
class UserDoesNotExistsException(ApplicationException):

    @property
    def title(self) -> str:
        return f"Пользователь не найден"


@dataclass(eq=False)
class UserAlreadyExistsException(ApplicationException):
    email: str

    @property
    def title(self) -> str:
        return f"Пользователь с данным e-mail уже существует: {self.email}"


@dataclass(eq=False)
class UserAlreadyVerifiedException(ApplicationException):

    @property
    def title(self) -> str:
        return f"Пользователь уже подтвержден"


@dataclass(eq=False)
class UserInactiveException(ApplicationException):

    @property
    def title(self) -> str:
        return f"Пользователь неактивен"


@dataclass(eq=False)
class InvalidAccessTokenException(ApplicationException):
    token: str

    @property
    def title(self) -> str:
        return f"Невалидный access-token: {self.token}"


@dataclass(eq=False)
class InvalidResetPasswordTokenException(ApplicationException):
    token: str

    @property
    def title(self) -> str:
        return f"Невалидный reset-password-token: {self.token}"


@dataclass(eq=False)
class InvalidUserIDException(ApplicationException):

    @property
    def title(self) -> str:
        return f"Неверный ID"
