from typing import Annotated

from fastapi import APIRouter, Depends

from src.application.common.dto import Pagination
from src.application.token.dto import (
    GetTokensFilters,
    TokenDTO,
    TokensPageDTO,
)
from src.presentation.api.dependencies.services import (
    GetTokenByAddressHandlerDep,
    GetTokensHandlerDep,
)
from src.presentation.api.schemas.response import (
    ApiResponse,
)

router = APIRouter(
    prefix="/tokens",
    tags=["Токены"],
    # dependencies=[Depends(get_current_user),]
)


@router.get(
    "/{token_address}",
    description="Возвращает токен с указанным адресом",
    summary="Получить токен по адресу",
    response_description="Детальная информация о токене.",
)
async def get_token(
    address: str,
    handler: GetTokenByAddressHandlerDep,
) -> ApiResponse[TokenDTO]:
    result = await handler(address=address)
    return ApiResponse(result=result)


@router.get(
    "",
    description="Возвращает список всех токенов с использованием limit и offset",
    summary="Получить список токенов",
    response_description="Список токенов с их детальной информацией.",
)
async def get_tokens(
    pagination: Annotated[Pagination, Depends()],
    filters: Annotated[GetTokensFilters, Depends()],
    handler: GetTokensHandlerDep,
) -> ApiResponse[TokensPageDTO]:
    result: TokensPageDTO = await handler(
        pagination=pagination,
        filters=filters,
    )
    return ApiResponse(result=result)
