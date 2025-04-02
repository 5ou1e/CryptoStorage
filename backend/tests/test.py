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
    Join,
)
from sqlalchemy.orm import registry, joinedload

from src.application.wallet.dto import GetWalletsFilters
from src.domain.entities import Swap as SwapEntity
from src.domain.entities import SwapEventType
from src.infra.db.sqlalchemy.models import Swap, Wallet, WalletStatistic30d, WalletStatisticAll
from src.infra.db.sqlalchemy.readers.wallet import GetWalletsFilterSet
from src.infra.db.sqlalchemy.repositories import SQLAlchemyWalletRepository, SQLAlchemyWalletStatisticAllRepository
from src.infra.db.sqlalchemy.setup import AsyncSessionLocal


def init_orm_mappers():
    mapper_registry = registry()

    mapper_registry.map_imperatively(
        SwapEntity,
        Swap.__table__,
    )


from sqlalchemy.orm import contains_eager


async def main():
    async with AsyncSessionLocal() as session:
        query = select(Wallet)
        query = query.options(
            # joinedload(Wallet.stats_all, innerjoin=True),
            #     contains_eager(Wallet.stats_30d)
        )
        # query = query.join(Wallet.stats_30d, isouter=True).filter(WalletStatistic30d.winrate >= 50.0)
        # print(list(query.get_final_froms()))
        filters = GetWalletsFilters(stats_all__winrate__gte=99, stats_all__winrate__lte=100)
        print(GetWalletsFilterSet.get_filters())

        filter_set = GetWalletsFilterSet(session, query)
        count_query = filter_set.count_query(filters.model_dump(exclude_none=True))
        print(count_query)
        query = filter_set.filter_query(filters.model_dump(exclude_none=True))
        print(list(query.get_final_froms()))
        return
        joined_before = False
        to_check = list(query.get_final_froms())
        print(to_check)
        while to_check:
            element = to_check.pop()
            if not isinstance(element, Join):
                continue
            if element.right == WalletStatisticAll.__table__ and element.onclause is not None:
                print("VOT ONA")
                joined_before = True

            to_check.append(element.left)
            to_check.append(element.right)

        if joined_before:
            query = query.options(contains_eager(Wallet.stats_all))
        else:
            query = query.options(joinedload(Wallet.stats_all))

        print(query)

        res = (await session.scalars(query.limit(1))).all()

        print(res[0].stats_all.total_token)


if __name__ == "__main__":
    start = datetime.now()
    asyncio.run(main())
    # print(datetime.now() - start)
