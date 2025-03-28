from fastapi import APIRouter
from src.settings import config
from starlette.responses import RedirectResponse

router = APIRouter()


@router.get("/", include_in_schema=False)
async def root() -> RedirectResponse:
    # Редирект с главной страницы на /docs
    return RedirectResponse(url=f"{config.api.prefix}/docs")
