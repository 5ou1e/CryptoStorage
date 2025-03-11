import asyncio
import logging

import aiohttp
from tortoise import Tortoise

from src.infra.db.models.tortoise import Swap
from src.infra.db.setup_tortoise import (
    init_db_async,
)
from src.settings import config

logger = logging.getLogger()
logger.setLevel(logging.INFO)

BATCH_SIZE = 1  # Размер пачки


async def get_transaction(session, tx_hash):
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getTransaction",
        "params": [
            tx_hash,
            {
                "encoding": "json",
                "maxSupportedTransactionVersion": 0,
            },
        ],
    }
    try:
        async with session.post(
            config.solana.rpc_node_url,
            json=payload,
            timeout=5,
        ) as response:
            response.raise_for_status()
            json_data = await response.json()
            return json_data.get("result", {})
    except Exception as e:
        logger.error(f"Ошибка запроса для {tx_hash}: {e}")
        return {}


async def get_swap_block_id(session, swap):
    transaction_data = await get_transaction(session, swap.tx_hash)
    return swap, transaction_data.get("slot")


async def process():
    while True:
        swaps = await Swap.filter(block_id=None).limit(BATCH_SIZE)
        if not swaps:
            break

        async with aiohttp.ClientSession() as session:
            tasks = [get_swap_block_id(session, swap) for swap in swaps]
            results = await asyncio.gather(*tasks, return_exceptions=True)

        # Обновляем только успешные
        updates = [swap for swap, block_id in results if block_id is not None]
        for swap, block_id in results:
            if block_id is not None:
                swap.block_id = block_id

        if updates:
            await Swap.bulk_update(updates, fields=["block_id"])
            logger.info(f"Обработано {len(updates)} транзакций")


async def main():
    await init_db_async()
    try:
        await process()
    finally:
        await Tortoise.close_connections()


if __name__ == "__main__":
    asyncio.run(main())
