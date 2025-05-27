import logging
from typing import Annotated

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Body, Depends, Query

from src.application.common.dto import Pagination
from src.application.handlers.wallet.commands.refresh_wallet_stats import (
    RefreshWalletStatsCommandHandler,
    RefreshWalletStatsResponse,
)
from src.application.handlers.wallet.dto import (
    GetWalletActivitiesFilters,
    GetWalletsFilters,
    GetWalletTokensFilters,
    WalletActivitiesPageDTO,
    WalletDTO,
    WalletRelatedWalletsDTO,
    WalletsPageDTO,
    WalletTokensPageDTO,
)
from src.application.handlers.wallet.dto.wallet import GetWalletsSorting
from src.application.handlers.wallet.dto.wallet_activity import GetWalletActivitiesSorting
from src.application.handlers.wallet.dto.wallet_token import GetWalletTokensSorting
from src.application.handlers.wallet.queries.get_refresh_wallet_stats_status import (
    GetRefreshWalletStatsStatusHandler,
    GetRefreshWalletStatsStatusResponse,
)
from src.application.handlers.wallet.queries.get_wallet_activities import GetWalletActivitiesHandler
from src.application.handlers.wallet.queries.get_wallet_by_address import GetWalletByAddressHandler
from src.application.handlers.wallet.queries.get_wallet_related_wallets import GetWalletRelatedWalletsHandler
from src.application.handlers.wallet.queries.get_wallet_tokens import GetWalletTokensHandler
from src.application.handlers.wallet.queries.get_wallets import GetWalletsHandler
from src.infra.redis.cache_service import RedisCacheService
from src.presentation.api.schemas.response import ApiResponse

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/wallets",
    tags=["Кошельки"],
)


@router.get(
    "/{address}",
    description="Возвращает кошелек с указанным адресом",
    summary="Получить кошелек по адресу",
    response_description="Детальная информация о кошельке.",
)
@inject
async def get_wallet_by_address(address: str, handler: FromDishka[GetWalletByAddressHandler]) -> ApiResponse[WalletDTO]:
    result = await handler(address)
    return ApiResponse(result=result)


@router.get(
    "",
    description="Возвращает список кошельков",
    summary="Получить список кошельков",
    response_description="Список кошельков с их детальной информацией.",
)
@inject
async def get_wallets(
    pagination: Annotated[Pagination, Depends()],
    sorting: Annotated[GetWalletsSorting, Depends()],
    filters: Annotated[GetWalletsFilters, Depends()],
    handler: FromDishka[GetWalletsHandler],
) -> ApiResponse[WalletsPageDTO]:
    result: WalletsPageDTO = await handler(pagination, filters, sorting)
    return ApiResponse(result=result)


@router.get(
    "/{address}/tokens",
    description="Возвращает обьект со списком токенов кошелька",
    summary="Получить токены кошелька по его адресу",
    response_description="Токены кошелька с детальной информацией",
)
@inject
async def get_wallet_tokens(
    address: str,
    pagination: Annotated[Pagination, Depends()],
    sorting: Annotated[GetWalletTokensSorting, Depends()],
    filters: Annotated[GetWalletTokensFilters, Depends()],
    handler: FromDishka[GetWalletTokensHandler],
) -> ApiResponse[WalletTokensPageDTO]:
    result: WalletTokensPageDTO = await handler(
        address,
        pagination,
        filters,
        sorting,
    )
    return ApiResponse(result=result)


@router.get(
    "/{address}/activities",
    description="Возвращает обьект со списком активностей кошелька",
    summary="Получить активности кошелька по его адресу",
    response_description="Активности с детальной информацией",
)
@inject
async def get_wallet_activities(
    address: str,
    pagination: Annotated[Pagination, Depends()],
    sorting: Annotated[GetWalletActivitiesSorting, Depends()],
    filters: Annotated[GetWalletActivitiesFilters, Depends()],
    handler: FromDishka[GetWalletActivitiesHandler],
) -> ApiResponse[WalletActivitiesPageDTO]:
    result: WalletActivitiesPageDTO = await handler(
        address,
        pagination,
        filters,
        sorting,
    )
    return ApiResponse(result=result)


@router.get(
    "/{address}/related_wallets",
    description="Возвращает связанные кошельки для кошелька",
    summary="Получить связанные кошельки по адресу кошелька",
    response_description="Список связанных кошельков",
)
@inject
async def get_wallet_related_wallets(
    address: str,
    handler: FromDishka[GetWalletRelatedWalletsHandler],
    cache_service: FromDishka[RedisCacheService],
) -> ApiResponse[WalletRelatedWalletsDTO]:
    key = f"get_wallet_related_wallets:{address}"
    result = await cache_service.get(key)

    if result is None:
        result = await handler(address)
        await cache_service.set(key, result.model_dump(mode="json"), expire=300)

    return ApiResponse(result=result)


@router.post(
    "/refresh_stats",
    description="Запросить обновление статистики кошелька",
    summary="Запросить обновление статистики кошелька",
)
@inject
async def create_refresh_wallet_stats_task(
    address: Annotated[str, Body(embed=True)],
    handler: FromDishka[RefreshWalletStatsCommandHandler],
) -> ApiResponse[RefreshWalletStatsResponse]:
    result = await handler(address)
    return ApiResponse(result=result)


@router.get(
    "/refresh_stats/{task_id}/status",
    description="Получить статус задачи обновления статистики кошелька",
    summary="Получить статус задачи обновления статистики кошелька",
)
@inject
async def get_wallet_refresh_stats_task_status(
    task_id: str,
    handler: FromDishka[GetRefreshWalletStatsStatusHandler],
) -> ApiResponse[GetRefreshWalletStatsStatusResponse]:
    result = await handler(task_id)
    return ApiResponse(result=result)
