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


@dataclass(kw_only=True)
class SwapEntity:
    field1: str
    field2: str
    field3: str
    field4: str
    field5: str


start = datetime.now()
for i in range(2_000_000):
    s = Swap(
        field1='str',
        field2='str',
        field3='str',
        field4='str',
        field5='str'
    )
print(datetime.now()-start)
