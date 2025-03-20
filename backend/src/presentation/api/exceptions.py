import json
import traceback
from collections import defaultdict
from functools import partial

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import ORJSONResponse
from starlette import status

from src.application.exceptions import ApplicationException
from src.application.token.exceptions import TokenNotFoundException
from src.application.wallet.exceptions import WalletNotFoundException
from src.presentation.api.schemas.response import ApiResponse


def setup_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(WalletNotFoundException, exception_handler(status.HTTP_404_NOT_FOUND))
    app.add_exception_handler(TokenNotFoundException, exception_handler(status.HTTP_404_NOT_FOUND))
    app.add_exception_handler(ApplicationException, exception_handler(500))
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, unknown_exception_handler)


def exception_handler(status_code: int):
    return partial(application_exception_handler, status_code=status_code)


async def application_exception_handler(
    request: Request, exc: ApplicationException, status_code: int
) -> ORJSONResponse:
    """Обработчик ошибок приложения"""
    response = ApiResponse(
        status="error",
        message=exc.title,
    )
    return ORJSONResponse(
        response.model_dump(),
        status_code=500,
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError | Exception) -> ORJSONResponse:
    """Обработчик ошибок валидации"""
    reformatted_message = defaultdict(list)
    for pydantic_error in exc.errors():
        loc, msg = pydantic_error["loc"], pydantic_error["msg"]
        filtered_loc = loc[1:] if loc[0] in ("body", "query", "path") else loc
        field_string = ".".join(filtered_loc)  # nested fields with dot-notation
        reformatted_message[field_string].append(msg)
    response = ApiResponse(status="error", message=json.dumps(reformatted_message))
    return ORJSONResponse(
        response.model_dump(),
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    )


async def unknown_exception_handler(request: Request, exc: Exception) -> ORJSONResponse:
    """Обработчик неизвестных ошибок"""
    traceback_str = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
    response = ApiResponse(status="error", message=f"Внутренняя ошибка сервера {traceback_str[-200:]}")
    return ORJSONResponse(
        response.model_dump(),
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
