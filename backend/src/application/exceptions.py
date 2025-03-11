from dataclasses import dataclass


@dataclass(eq=False)
class ApplicationException(Exception):
    """Базовая ошибка приложения"""

    @property
    def title(self) -> str:
        return f"Ошибка приложения"
