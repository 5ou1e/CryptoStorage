import asyncio
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import TypedDict
from uuid import UUID

from sqlalchemy import MetaData, Table, Column, Integer, String, Text, ForeignKey, DateTime, select
from sqlalchemy.orm import registry
from src.domain.entities import Swap as SwapEventType
from src.infra.db.sqlalchemy.models import Swap
from src.infra.db.sqlalchemy.setup import AsyncSessionLocal


class SwapEntity(TypedDict):
    id: UUID
    wallet_id: UUID
    token_id: UUID
    tx_hash: str
    block_id: int
    timestamp: datetime | None
    event_type: SwapEventType | None
    quote_amount: Decimal | None
    token_amount: Decimal | None
    price_usd: Decimal | None
    is_part_of_transaction_with_mt_3_swappers: bool
    is_part_of_arbitrage_swap_event: bool
    created_at:datetime
    updated_at: datetime


def init_orm_mappers():
    mapper_registry = registry()

    mapper_registry.map_imperatively(
        SwapEntity,
        Swap.__table__,
    )


async def main():
    init_orm_mappers()
    async with AsyncSessionLocal() as session:
        query = select(SwapEntity).limit(1000)
        res = await session.execute(query)
        swaps = res.scalars().all()
        print(swaps[0])

if __name__ == "__main__":
    start = datetime.now()
    asyncio.run(main())
    print(datetime.now()-start)
