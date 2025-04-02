import dataclasses
import uuid
from typing import Any, Optional

from fastapi import APIRouter, Depends, Query
from pydantic import Field, BaseModel
from sqlalchemy import select

from src.application.wallet.queries.get_wallet_by_address import (
    GetWalletByAddressHandler,
)
from src.infra.celery.tasks import update_single_wallet_statistics_task
from src.infra.db.sqlalchemy.models import Wallet, WalletStatistic30d
from src.infra.db.sqlalchemy.readers import SQLAlchemyWalletReader
from src.infra.db.sqlalchemy.repositories import SQLAlchemyWalletRepository
from src.infra.db.sqlalchemy.setup import get_db_session, AsyncSessionLocal
from src.presentation.api.schemas.response import ApiResponse
from pydantic import parse_obj_as

router = APIRouter(prefix="/test", tags=["Test endpoints"])
from typing import Optional, Any, Dict

from sqlalchemy import select, Select
from sqlalchemy_filterset.types import ModelAttribute

from src.infra.db.sqlalchemy.models import Swap, Wallet, WalletToken, WalletStatistic30d

from sqlalchemy_filterset import (
    Filter,
    InFilter,
    JoinStrategy,
    LimitOffsetFilter,
    MultiJoinStrategy,
    OrderingField,
    OrderingFilter,
    RangeFilter,
    SearchFilter,
    AsyncFilterSet,
    BaseFilter,
    BaseStrategy,
)

import operator as op


class GreaterThanOrEqualFilter(BaseFilter):
    """Фильтр для значений больше или равно (>=)."""

    def __init__(
        self,
        field: ModelAttribute,
        strategy: Optional[BaseStrategy] = None,
    ) -> None:
        super().__init__()
        self.field = field
        self.strategy = strategy if strategy is not None else BaseStrategy()

    def filter(self, query: Select, value: Optional[Any], values: Dict[str, Any]) -> Select:
        if value is None:
            return query
        return self.strategy.filter(query, op.ge(self.field, value))


class WalletFilterSet(AsyncFilterSet):
    address = Filter(Wallet.address)
    stats_30d__total_token = GreaterThanOrEqualFilter(
        WalletStatistic30d.total_token,
        strategy=JoinStrategy(
            WalletStatistic30d,
            Wallet.id == WalletStatistic30d.wallet_id,
        ),
    )


class WalletFilterSchema(BaseModel):
    address: Optional[str] = None
    stats_30d__total_token: int = None

    class Config:
        orm_mode = True


@router.get("/test", response_model=Any)
async def test(
    # filter_params: WalletFilterSchema = Depends(),
) -> Any:
    filter_params = WalletFilterSchema(
        # address=None,
        stats_30d__total_token=100,
    )
    async with AsyncSessionLocal() as session:
        filter_set = WalletFilterSet(session, select(Wallet))
        # filter_params = parse_obj_as(WalletFilterSchema, filters)
        filtered_wallets_query = filter_set.filter_query(filter_params.dict(exclude_none=True))
        print(filtered_wallets_query)

        filtered_wallets = await filter_set.filter(filter_params.dict(exclude_none=True))
        print(type(filtered_wallets[0]))
        repo = SQLAlchemyWalletRepository(session)
        # print(filtered_wallets)
        return repo.model_to_entity((filtered_wallets[0]))


@router.post("/tasks/start")
async def start_task(address: str):
    from src.infra.db.sqlalchemy.setup import engine

    print(f"Engine ID: {id(engine)}")
    task = update_single_wallet_statistics_task.apply_async(args=[address])  # Запускаем задачу Celery
    return {"task_id": task.id}


@router.get("/tasks/status/{task_id}")
async def task_status(task_id: str):
    task = update_single_wallet_statistics_task.AsyncResult(task_id)
    return {"status": task.status, "result": task.result if task.ready() else None}
