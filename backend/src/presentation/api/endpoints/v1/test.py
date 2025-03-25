from typing import Any, Optional

from fastapi import APIRouter
from fastapi_filter.contrib.sqlalchemy import Filter

from src.application.wallet.queries.get_wallet_by_address import GetWalletByAddressHandler
from src.infra.db.sqlalchemy.models import Wallet
from src.infra.db.sqlalchemy.readers import SQLAlchemyWalletReader
from src.infra.db.sqlalchemy.repositories import SQLAlchemyWalletRepository
from src.infra.db.sqlalchemy.setup import get_db_session
from src.presentation.api.schemas.response import ApiResponse

router = APIRouter(prefix="/test", tags=["Test endpoints"])


class WalletFilter(Filter):
    address: Optional[str] = None
    # details: Optional[WalletDetailFilter] = FilterDepends(with_prefix("details", WalletDetailFilter))
    is_bot: Optional[bool]

    class Constants(Filter.Constants):
        model = Wallet


@router.get("/test", response_model=Any)
async def test() -> Any:
    session = get_db_session()
    async for session in get_db_session():
        reader = SQLAlchemyWalletReader(session)
        service = GetWalletByAddressHandler(reader)
        result = await service(address="12312312")
        return ApiResponse(result=result)
