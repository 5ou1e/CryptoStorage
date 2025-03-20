import asyncio
import time
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime
from decimal import Decimal
from functools import partial
from typing import Optional, TypedDict
from uuid import UUID

import uuid6

from src.domain.entities.wallet import WalletStatisticAllEntity


def load_data_to_db(objects):
    print("ХОБА")
    return objects


class WalletStatisticAllEntityDict(TypedDict):
    wallet_id: Optional[UUID]
    winrate: Optional[Decimal]
    total_token_buy_amount_usd: Optional[Decimal]
    total_token_sell_amount_usd: Optional[Decimal]
    total_profit_usd: Optional[Decimal]
    total_profit_multiplier: Optional[float]
    total_token: Optional[int]
    total_token_buys: Optional[int]
    total_token_sales: Optional[int]
    token_with_buy_and_sell: Optional[int]
    token_with_buy: Optional[int]
    token_sell_without_buy: Optional[int]
    token_buy_without_sell: Optional[int]
    token_with_sell_amount_gt_buy_amount: Optional[int]
    token_avg_buy_amount: Optional[Decimal]
    token_median_buy_amount: Optional[Decimal]
    token_first_buy_avg_price_usd: Optional[Decimal]
    token_first_buy_median_price_usd: Optional[Decimal]
    token_avg_profit_usd: Optional[Decimal]
    token_buy_sell_duration_avg: Optional[int]
    token_buy_sell_duration_median: Optional[int]
    pnl_lt_minus_dot5_num: Optional[int]
    pnl_minus_dot5_0x_num: Optional[int]
    pnl_lt_2x_num: Optional[int]
    pnl_2x_5x_num: Optional[int]
    pnl_gt_5x_num: Optional[int]
    pnl_lt_minus_dot5_percent: Optional[float]
    pnl_minus_dot5_0x_percent: Optional[float]
    pnl_lt_2x_percent: Optional[float]
    pnl_2x_5x_percent: Optional[float]
    pnl_gt_5x_percent: Optional[float]
    total_swaps_from_arbitrage_swap_events: Optional[int]
    total_swaps_from_txs_with_mt_3_swappers: Optional[int]


async def load_process():
    created = datetime.now()
    objects_to_load = [
        WalletStatisticAllEntity(
            wallet_id=uuid6.uuid7,
            created_at=created,
            updated_at=created,
            winrate=123,
            total_token_buy_amount_usd=123,
            total_token_sell_amount_usd=123,
            total_profit_usd=123,
            total_profit_multiplier=123,
            total_token=123,
            total_token_buys=123,
            total_token_sales=123,
            token_with_buy_and_sell=123,
            token_with_buy=123,
            token_sell_without_buy=123,
            token_buy_without_sell=123,
            token_with_sell_amount_gt_buy_amount=123,
            token_avg_buy_amount=123,
            token_median_buy_amount=123,
            token_first_buy_avg_price_usd=123,
            token_first_buy_median_price_usd=123,
            token_avg_profit_usd=123,
            token_buy_sell_duration_avg=123,
            token_buy_sell_duration_median=123,
            pnl_lt_minus_dot5_num=123,
            pnl_minus_dot5_0x_num=123,
            pnl_lt_2x_num=123,
            pnl_2x_5x_num=123,
            pnl_gt_5x_num=123,
            pnl_lt_minus_dot5_percent=123,
            pnl_minus_dot5_0x_percent=123,
            pnl_lt_2x_percent=123,
            pnl_2x_5x_percent=123,
            pnl_gt_5x_percent=123,
            total_swaps_from_arbitrage_swap_events=123,
            total_swaps_from_txs_with_mt_3_swappers=123,
        )
        for i in range(1000000)
    ]
    start = datetime.now()
    for obj in objects_to_load:
        obj.to_dict()
    end = datetime.now()
    print(f"Время: {end - start}")
    time.sleep(100)


if __name__ == "__main__":
    asyncio.run(load_process())
