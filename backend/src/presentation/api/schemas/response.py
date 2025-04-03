from typing import Any, Generic, Optional, TypeVar

from pydantic import BaseModel

TResult = TypeVar("TResult")


class ApiResponse(BaseModel, Generic[TResult]):
    status: str = "success"
    result: Optional[TResult] = None
    message: Optional[str] = ""
    details: Optional[Any] = None  # Детали ошибок

