import logging
from typing import Annotated

from fastapi import APIRouter, Depends
from src.application.common.dto import Pagination
from src.application.wallet.dto import (
    GetWalletActivitiesFilters,
    GetWalletsFilters,
    GetWalletTokensFilters,
    WalletActivitiesPageDTO,
    WalletDTO,
    WalletRelatedWalletsDTO,
    WalletsPageDTO,
    WalletTokensPageDTO,
)
from src.presentation.api.dependencies.services import (
    GetWalletActivitiesHandlerDep,
    GetWalletByAddressHandlerDep,
    GetWalletRelatedWalletsHandlerDep,
    GetWalletsHandlerDep,
    GetWalletTokensHandlerDep,
)
from src.presentation.api.schemas.response import ApiResponse

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/wallets",
    tags=["Кошельки"],
    # dependencies=[Depends(get_current_user),]
)


@router.get(
    "/{address}",
    description="Возвращает кошелек с указанным адресом",
    summary="Получить кошелек по адресу",
    response_description="Детальная информация о кошельке.",
)
async def get_wallet_by_address(
    address: str,
    handler: GetWalletByAddressHandlerDep,
) -> ApiResponse[WalletDTO]:
    result = await handler(address)
    return ApiResponse(result=result)


@router.get(
    "",
    description="Возвращает список всех кошельков с использованием limit и offset",
    summary="Получить список кошельков",
    response_description="Список кошельков с их детальной информацией.",
)
async def get_wallets(
    pagination: Annotated[Pagination, Depends()],
    filters: Annotated[GetWalletsFilters, Depends()],
    handler: GetWalletsHandlerDep,
) -> ApiResponse[WalletsPageDTO]:
    result: WalletsPageDTO = await handler(
        pagination,
        filters,
    )
    return ApiResponse(result=result)


@router.get(
    "/{address}/tokens",
    description="Возвращает обьект со списком токенов кошелька",
    summary="Получить токены кошелька по его адресу",
    response_description="Токены кошелька с детальной информацией",
)
async def get_wallet_tokens(
    address: str,
    pagination: Annotated[Pagination, Depends()],
    filters: Annotated[GetWalletTokensFilters, Depends()],
    handler: GetWalletTokensHandlerDep,
) -> ApiResponse[WalletTokensPageDTO]:
    result: WalletTokensPageDTO = await handler(
        address,
        pagination,
        filters,
    )
    return ApiResponse(result=result)


@router.get(
    "/{address}/activities",
    description="Возвращает обьект со списком активностей кошелька",
    summary="Получить активности кошелька по его адресу",
    response_description="Активности с детальной информацией",
)
async def get_wallet_activities(
    address: str,
    pagination: Annotated[Pagination, Depends()],
    filters: Annotated[GetWalletActivitiesFilters, Depends()],
    handler: GetWalletActivitiesHandlerDep,
) -> ApiResponse[WalletActivitiesPageDTO]:
    result: WalletActivitiesPageDTO = await handler(
        address,
        pagination,
        filters,
    )
    return ApiResponse(result=result)


@router.get(
    "/{address}/related_wallets",
    description="Возвращает связанные кошельки для кошелька по адресу",
    summary="Получить связанные кошельки по адресу кошелька",
    response_description="Список связанных кошельков",
)
async def get_wallet_related_wallets(
    address: str,
    handler: GetWalletRelatedWalletsHandlerDep,
) -> ApiResponse[WalletRelatedWalletsDTO]:
    result: WalletRelatedWalletsDTO = await handler(address)
    return ApiResponse(result=result)
