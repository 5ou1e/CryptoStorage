from typing import Annotated

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Depends

from src.application.common.dto import Pagination
from src.application.token.dto import GetTokensFilters, TokenDTO, TokensPageDTO
from src.application.token.queries.get_token_by_address import GetTokenByAddressHandler
from src.application.token.queries.get_tokens import GetTokensHandler
from src.presentation.api.schemas.response import ApiResponse

router = APIRouter(
    prefix="/tokens",
    tags=["Токены"],
)


@router.get(
    "/{token_address}",
    description="Возвращает токен с указанным адресом",
    summary="Получить токен по адресу",
    response_description="Детальная информация о токене.",
)
@inject
async def get_token(
    address: str,
    handler: FromDishka[GetTokenByAddressHandler],
) -> ApiResponse[TokenDTO]:
    result = await handler(address=address)
    return ApiResponse(result=result)


@router.get(
    "",
    description="Возвращает список всех токенов",
    summary="Получить список токенов",
    response_description="Список токенов с их детальной информацией.",
)
@inject
async def get_tokens(
    pagination: Annotated[Pagination, Depends()],
    filters: Annotated[GetTokensFilters, Depends()],
    handler: FromDishka[GetTokensHandler],
) -> ApiResponse[TokensPageDTO]:
    result: TokensPageDTO = await handler(
        pagination=pagination,
        filters=filters,
    )
    return ApiResponse(result=result)
