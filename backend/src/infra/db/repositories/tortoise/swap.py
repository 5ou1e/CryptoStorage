from typing import List, Optional

from src.application.interfaces.repositories.swap import BaseSwapRepository
from src.domain.entities.swap import SwapEntity
from src.infra.db.models.tortoise.swap import Swap

from .generic_repository import TortoiseGenericRepository


class TortoiseSwapRepository(TortoiseGenericRepository, BaseSwapRepository):
    model_class = Swap
    entity_class = SwapEntity

    async def get_first_by_wallet_and_token(
        self,
        wallet_id: str,
        token_id: str,
        event_type: str | None = None,
    ):
        """Возвращает первую по block_id swap операцию (buy/sell) для заданного кошелька и токена"""
        query = self.model.filter(
            wallet_id=wallet_id,
            token_id=token_id,
        ).order_by("block_id")
        if event_type:
            query = query.filter(event_type=event_type)
        return await query.first()

    async def get_neighbors_by_token(
        self,
        token_id: str,
        block_id: int,
        event_type: str | None = None,
        blocks_before: int = 3,
        blocks_after: int = 3,
        exclude_wallets: Optional[List] = None,
    ):
        """Возвращает соседние сделки (buy/sell) по токену в заданном диапазоне блоков"""
        query = self.model.filter(
            token_id=token_id,
            block_id__gte=block_id - blocks_before,
            block_id__lte=block_id + blocks_after,
            event_type=event_type,
        )
        if event_type:
            query = query.filter(event_type=event_type)
        if exclude_wallets:
            query = query.filter(wallet_id__not_in=exclude_wallets)
        return await query.all()
