import asyncio
import logging

from tortoise import Tortoise

from src.infra.db.models.tortoise import Swap, WalletToken
from src.infra.db.setup_tortoise import init_db_async

logger = logging.getLogger()
logger.setLevel(logging.INFO)

TIMESTAMP_FROM: int = "timestamp_from"


async def process():
    swaps = await Swap.filter(timestamp__gte=TIMESTAMP_FROM).order_by("timestamp").all()
    print(len(swaps))
    processed = 0
    for activity in swaps[1:]:
        stats = await WalletToken.filter(
            token_id=activity.token_id,
            wallet_id=activity.wallet_id,
        ).first()
        if activity.event_type == "buy":
            stats.total_buys_count -= 1
            stats.total_buy_amount_usd -= activity.cost_usd if activity.cost_usd else 0
            stats.total_buy_amount_token -= activity.token_amount if activity.token_amount else 0
        else:
            stats.total_sales_count -= 1
            stats.total_sell_amount_usd -= activity.cost_usd if activity.cost_usd else 0
            stats.total_sell_amount_token -= activity.token_amount if activity.token_amount else 0

        if activity.is_part_of_transaction_with_mt_3_swappers:
            stats.total_swaps_from_txs_with_mt_3_swappers -= 1
        if activity.is_part_of_arbitrage_swap_event:
            stats.total_swaps_from_arbitrage_swap_events -= 1
        await stats.save()
        # print(activity.__dict__)
        # print(stats.__dict__)
        processed += 1
        print(processed)


async def main():
    await init_db_async()
    try:
        await process()
    finally:
        await Tortoise.close_connections()


if __name__ == "__main__":
    asyncio.run(main())
