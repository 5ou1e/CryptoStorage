from abc import ABC
from typing import List, Optional

from src.domain.entities.swap import SwapEntity

from .generic_repository import BaseGenericRepository


class BaseSwapRepository(BaseGenericRepository[SwapEntity], ABC):
    """Интерфейс репозитория Swap"""

    async def get_first_by_wallet_and_token(
        self,
        wallet_id: str,
        token_id: str,
        event_type: str | None = None,
    ) -> SwapEntity | None:
        """Возвращает первую по block_id swap операцию (buy/sell) для заданного кошелька и токена"""
        raise NotImplementedError

    async def get_neighbors_by_token(
        self,
        token_id: str,
        block_id: int,
        event_type: str | None = None,
        blocks_before: int = 3,
        blocks_after: int = 3,
        exclude_wallets: Optional[List] = None,
    ) -> List[SwapEntity]:
        """Возвращает соседние сделки (buy/sell) по токену в заданном диапазоне блоков"""
        raise NotImplementedError
