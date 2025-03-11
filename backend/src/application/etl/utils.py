import logging
import statistics
from datetime import datetime, timedelta

import pytz

logger = logging.getLogger("tasks.update_wallet_statistics")


async def filter_period_tokens(all_tokens, period, current_datetime) -> list:
    """ "Фильтруем только те токены у которых первая покупка попадает в диапазон и до нее нет продаж"""
    if period == 0:
        return all_tokens
    days = int(period)
    threshold_date = current_datetime - timedelta(days=days)

    period_tokens = []
    for token in all_tokens:
        fb_datetime = (
            datetime.fromtimestamp(
                int(token.first_buy_timestamp),
                tz=pytz.UTC,
            )
            if token.first_buy_timestamp
            else None
        )
        fs_datetime = (
            datetime.fromtimestamp(
                int(token.first_sell_timestamp),
                tz=pytz.UTC,
            )
            if token.first_sell_timestamp
            else None
        )
        if (fb_datetime and fb_datetime >= threshold_date) and (fs_datetime is None or fs_datetime >= threshold_date):
            period_tokens.append(token)
        elif fs_datetime and fs_datetime >= threshold_date:
            period_tokens.append(token)

    return period_tokens


async def recalculate_wallet_period_stats(stats, token_stats):
    total_token = 0
    total_token_buys = 0
    total_token_sales = 0
    total_token_buy_amount_usd = 0
    total_token_sell_amount_usd = 0
    total_profit_usd = 0
    pnl_lt_minus_dot5_num = 0
    pnl_minus_dot5_0x_num = 0
    pnl_lt_2x_num = 0
    pnl_2x_5x_num = 0
    pnl_gt_5x_num = 0
    token_with_buy = 0
    token_with_buy_and_sell = 0
    token_buy_without_sell = 0
    token_sell_without_buy = 0
    token_with_sell_amount_gt_buy_amount = 0
    total_swaps_from_txs_with_mt_3_swappers = 0
    total_swaps_from_arbitrage_swap_events = 0

    profitable_tokens_count = 0
    token_first_buy_sell_duration_values = []
    token_buy_amount_usd_values = []
    token_first_buy_price_values = []

    for token in token_stats:
        total_token += 1
        total_token_buys += token.total_buys_count
        total_token_sales += token.total_sales_count
        total_token_buy_amount_usd += token.total_buy_amount_usd
        total_token_sell_amount_usd += token.total_sell_amount_usd
        total_profit_usd += token.total_profit_usd if token.total_profit_usd else 0

        total_swaps_from_txs_with_mt_3_swappers += token.total_swaps_from_txs_with_mt_3_swappers
        total_swaps_from_arbitrage_swap_events += token.total_swaps_from_arbitrage_swap_events

        if token.total_buys_count > 0:
            token_with_buy += 1
            if token.first_buy_price_usd:
                token_first_buy_price_values.append(token.first_buy_price_usd)
            if token.total_sales_count > 0:
                token_with_buy_and_sell += 1
            token_buy_amount_usd_values.append(token.total_buy_amount_usd)

        if token.total_buys_count > 0 and token.total_sales_count == 0:
            token_buy_without_sell += 1
        if token.total_sales_count > 0 and token.total_buys_count == 0:
            token_sell_without_buy += 1

        if token.total_buys_count:
            if token.total_sell_amount_token > token.total_buy_amount_token:
                token_with_sell_amount_gt_buy_amount += 1

        if token.first_buy_sell_duration is not None:
            token_first_buy_sell_duration_values.append(token.first_buy_sell_duration)

        profit_percent = token.total_profit_percent
        if token.total_buys_count > 0:
            if token.total_profit_usd >= 0:
                profitable_tokens_count += 1
            if profit_percent is not None:
                if profit_percent > 500:
                    pnl_gt_5x_num += 1
                elif profit_percent > 200:
                    pnl_2x_5x_num += 1
                elif profit_percent > 0:
                    pnl_lt_2x_num += 1
                elif profit_percent > -50:
                    pnl_minus_dot5_0x_num += 1
                else:
                    pnl_lt_minus_dot5_num += 1

    stats.total_token = total_token
    stats.total_token_buys = total_token_buys
    stats.total_token_sales = total_token_sales
    stats.total_token_buy_amount_usd = total_token_buy_amount_usd
    stats.total_token_sell_amount_usd = total_token_sell_amount_usd
    stats.total_profit_usd = total_profit_usd
    stats.pnl_lt_minus_dot5_num = pnl_lt_minus_dot5_num
    stats.pnl_minus_dot5_0x_num = pnl_minus_dot5_0x_num
    stats.pnl_lt_2x_num = pnl_lt_2x_num
    stats.pnl_2x_5x_num = pnl_2x_5x_num
    stats.pnl_gt_5x_num = pnl_gt_5x_num
    stats.token_with_buy = token_with_buy
    stats.token_with_buy_and_sell = token_with_buy_and_sell
    stats.token_buy_without_sell = token_buy_without_sell
    stats.token_sell_without_buy = token_sell_without_buy
    stats.token_with_sell_amount_gt_buy_amount = token_with_sell_amount_gt_buy_amount
    stats.total_swaps_from_txs_with_mt_3_swappers = total_swaps_from_txs_with_mt_3_swappers
    stats.total_swaps_from_arbitrage_swap_events = total_swaps_from_arbitrage_swap_events

    stats.total_profit_multiplier = (
        stats.total_profit_usd / stats.total_token_buy_amount_usd * 100 if stats.total_token_buy_amount_usd else None
    )  # Только для токенов у которых была покупка!

    stats.token_avg_buy_amount = (
        stats.total_token_buy_amount_usd / stats.token_with_buy if stats.token_with_buy else None
    )

    stats.token_first_buy_avg_price_usd = (
        sum(token_first_buy_price_values) / stats.token_with_buy if stats.token_with_buy else None
    )

    stats.token_first_buy_median_price_usd = (
        statistics.median(token_first_buy_price_values) if token_first_buy_price_values else None
    )

    stats.token_avg_profit_usd = (
        stats.total_profit_usd / stats.token_with_buy if stats.token_with_buy else None
    )  # Только для токенов у которых была покупка!

    stats.winrate = (
        profitable_tokens_count / stats.token_with_buy * 100 if stats.token_with_buy else None
    )  # Только для токенов у которых была покупка!

    stats.token_buy_sell_duration_avg = (
        sum(token_first_buy_sell_duration_values) / stats.token_with_buy_and_sell
        if stats.token_with_buy_and_sell
        else None
    )

    stats.token_buy_sell_duration_median = (
        statistics.median(token_first_buy_sell_duration_values) if token_first_buy_sell_duration_values else None
    )

    stats.token_median_buy_amount = (
        statistics.median(token_buy_amount_usd_values) if token_buy_amount_usd_values else None
    )

    if stats.token_with_buy:
        stats.pnl_lt_minus_dot5_percent = stats.pnl_lt_minus_dot5_num / stats.token_with_buy * 100
        stats.pnl_minus_dot5_0x_percent = stats.pnl_minus_dot5_0x_num / stats.token_with_buy * 100
        stats.pnl_lt_2x_percent = stats.pnl_lt_2x_num / stats.token_with_buy * 100
        stats.pnl_2x_5x_percent = stats.pnl_2x_5x_num / stats.token_with_buy * 100
        stats.pnl_gt_5x_percent = stats.pnl_gt_5x_num / stats.token_with_buy * 100

    return stats
