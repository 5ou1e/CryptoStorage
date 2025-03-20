from fastapi import APIRouter
from starlette.responses import RedirectResponse

from src.settings import config

router = APIRouter()


@router.get("/", include_in_schema=False)
async def root() -> RedirectResponse:
    # Редирект с главной страницы на /docs
    return RedirectResponse(url=f"{config.api.prefix}/docs")
