from collections import defaultdict
from datetime import datetime

import pytz

from src.domain.entities.swap import SwapEntity, SwapEventType
from src.domain.entities.wallet import WalletTokenEntity


def calculate_wallet_token(wt: WalletTokenEntity, activities: list[SwapEntity]) -> None:
    """Пересчитывает статистику для связки кошелька с токеном"""

    for activity in activities:
        if activity.event_type == SwapEventType.BUY:
            wt.total_buys_count += 1
            wt.total_buy_amount_usd += activity.price_usd * activity.quote_amount
            wt.total_buy_amount_token += activity.token_amount if activity.token_amount else 0
            if not wt.first_buy_timestamp or (activity.timestamp < wt.first_buy_timestamp):
                wt.first_buy_timestamp = activity.timestamp
                if activity.token_amount:
                    wt.first_buy_price_usd = activity.price_usd * activity.quote_amount / activity.token_amount
        elif activity.event_type == SwapEventType.SELL:
            wt.total_sales_count += 1
            wt.total_sell_amount_usd += activity.price_usd * activity.quote_amount
            wt.total_sell_amount_token += activity.token_amount if activity.token_amount else 0
            if not wt.first_sell_timestamp or (activity.timestamp < wt.first_sell_timestamp):
                wt.first_sell_timestamp = activity.timestamp
                if activity.token_amount:
                    wt.first_sell_price_usd = activity.price_usd * activity.quote_amount / activity.token_amount
        else:
            continue
        if not wt.last_activity_timestamp or (activity.timestamp > wt.last_activity_timestamp):
            wt.last_activity_timestamp = activity.timestamp

        if activity.is_part_of_transaction_with_mt_3_swappers:
            wt.total_swaps_from_txs_with_mt_3_swappers += 1
        if activity.is_part_of_arbitrage_swap_event:
            wt.total_swaps_from_arbitrage_swap_events += 1

    if wt.first_buy_timestamp and wt.first_sell_timestamp and (wt.first_buy_timestamp <= wt.first_sell_timestamp):
        wt.first_buy_sell_duration = int((wt.first_sell_timestamp - wt.first_buy_timestamp).total_seconds())
    if wt.total_buys_count > 0:
        wt.total_profit_usd = wt.total_sell_amount_usd - wt.total_buy_amount_usd
        wt.total_profit_percent = (
            round(
                wt.total_profit_usd / wt.total_buy_amount_usd * 100,
                2,
            )
            if not wt.total_buy_amount_usd == 0
            else None
        )

    wt.updated_at = datetime.now(pytz.timezone("Europe/Moscow"))


def calculate_wallet_tokens(wallet_tokens: list[WalletTokenEntity], activities: list[SwapEntity]):
    activity_map = defaultdict(list)
    for act in activities:
        activity_map[(act.wallet_id, act.token_id)].append(act)
    for wt in wallet_tokens:
        key = (wt.wallet_id, wt.token_id)
        activities = activity_map[key]
        calculate_wallet_token(wt, activities)
