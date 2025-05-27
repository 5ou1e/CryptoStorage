from pydantic import BaseModel

from src.infra.celery.tasks import update_single_wallet_statistics_task


class RefreshWalletStatsResponse(BaseModel):
    task_id: str


class RefreshWalletStatsCommandHandler:
    def __init__(self) -> None:
        pass

    async def __call__(self, address) -> RefreshWalletStatsResponse:
        task = update_single_wallet_statistics_task.apply_async(kwargs={"address": address})
        return RefreshWalletStatsResponse(task_id=task.id)
