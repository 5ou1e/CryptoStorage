import asyncio
from src.settings import logging

import warnings
warnings.filterwarnings(
    "ignore",
    message=".*pydantic.error_wrappers:ValidationError.*",
    category=UserWarning
)

from .parser import process


async def main():
    while True:
        await process()
        await asyncio.sleep(3600)


if __name__ == "__main__":
    # import logging
    # logging.basicConfig(
    #     format="%(asctime)s [%(levelname)s] %(message)s",
    #     level=logging.DEBUG,
    # )
    asyncio.run(main())
