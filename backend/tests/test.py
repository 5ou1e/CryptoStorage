import asyncio
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import TypedDict
from uuid import UUID

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    MetaData,
    String,
    Table,
    Text,
    select,
)
from sqlalchemy.orm import registry
from src.domain.entities import Swap as SwapEntity
from src.domain.entities import SwapEventType
from src.infra.db.sqlalchemy.models import Swap
from src.infra.db.sqlalchemy.repositories import SQLAlchemySwapRepository
from src.infra.db.sqlalchemy.setup import AsyncSessionLocal


def init_orm_mappers():
    mapper_registry = registry()

    mapper_registry.map_imperatively(
        SwapEntity,
        Swap.__table__,
    )


async def main():
    # init_orm_mappers()
    # async with AsyncSessionLocal() as session:
    #     res = await SQLAlchemySwapRepository(session).get_list(100_000)
    #     print(res[0])
    async with AsyncSessionLocal() as session:
        query = select(*Swap.__table__.columns).limit(100000)
        connection = await session.connection()
        res = await session.execute(query)
        swaps = [SwapEntity(**s) for s in res.mappings().all()]
        print(swaps[0])


if __name__ == "__main__":
    start = datetime.now()
    asyncio.run(main())
    print(datetime.now() - start)
