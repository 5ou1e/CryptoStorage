import asyncio
from datetime import datetime

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
from sqlalchemy.orm import registry, joinedload, contains_eager

from src.infra.db.sqlalchemy.models import Swap, Wallet, WalletStatistic30d, WalletStatisticAll
from src.infra.db.sqlalchemy.setup import AsyncSessionMaker

from dataclass_sqlalchemy_mixins.base import utils


async def main():
    async with AsyncSessionMaker() as session:
        query = select(Wallet)
        query = query.options(
            # joinedload(Wallet.stats_all, innerjoin=True),
            contains_eager(Wallet.stats_all)
        )

        filters = {
            "tokens__token__address__gte": 99,
        }

        binary_expressions = utils.get_binary_expressions(filters=filters, model=Wallet)

        order_by = ["id", "-created_at"]

        unary_expressions = utils.get_unary_expressions(
            order_by=order_by,
            model=Wallet,
        )

        query = query.order_by(*unary_expressions)

        print(binary_expressions)
        query = query.join(WalletStatisticAll).filter(*binary_expressions)

        print(query)


if __name__ == "__main__":
    start = datetime.now()
    asyncio.run(main())
    # print(datetime.now() - start)
