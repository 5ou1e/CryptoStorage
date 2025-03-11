from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Test:
    field1: str


start = datetime.now()
for i in range(10000000):
    t = Test(
        '123'
    )

print(datetime.now() - start)
