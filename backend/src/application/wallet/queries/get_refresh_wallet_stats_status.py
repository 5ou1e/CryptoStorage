from enum import StrEnum
from typing import Optional

from pydantic import BaseModel

from celery.result import AsyncResult

from src.application.wallet.exceptions import RefreshWalletStatsTaskNotFoundException
from src.infra.celery.setup import app as celery_app


class TaskStatus(StrEnum):
    success = "success"
    pending = "pending"
    failure = "failure"


class GetRefreshWalletStatsStatusResponse(BaseModel):
    task_id: str
    task_status: TaskStatus
    task_result: Optional[str] = None


class GetRefreshWalletStatsStatusHandler:
    def __init__(self) -> None:
        pass

    async def __call__(
        self,
        task_id
    ) -> GetRefreshWalletStatsStatusResponse:
        result = AsyncResult(task_id, app=celery_app)
        task_status = TaskStatus(str(result.status).lower())
        return GetRefreshWalletStatsStatusResponse(
            task_id=task_id,
            task_status=task_status,
            task_result=str(result.result)
        )
