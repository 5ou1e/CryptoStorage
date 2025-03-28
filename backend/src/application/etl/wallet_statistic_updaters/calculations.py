import statistics
from datetime import datetime, timedelta, timezone

import pytz
from src.domain.entities.wallet import Wallet, WalletStatisticAll


def calculate_wallet_stats(wallet):
    periods = [7, 30, 0]
    all_tokens = wallet.tokens
    current_datetime = datetime.now().astimezone(tz=pytz.UTC)
    for period in periods:
        if period == 7:
            stats = wallet.stats_7d
        elif period == 30:
            stats = wallet.stats_30d
        else:
            stats = wallet.stats_all
        token_stats = filter_period_tokens(all_tokens, period, current_datetime)
        recalculate_wallet_period_stats(stats, token_stats)

    wallet.is_scammer = determine_scammer_status(wallet)
    wallet.is_bot = determine_bot_status(wallet)


def determine_bot_status(
    wallet: Wallet,
) -> bool:
    """Определяем статус арбитраж-бота"""
    stats_all: WalletStatisticAll | None = wallet.stats_all
    # Если у кошелька более 50% активностей помечены как арбитражные - помечаем его как арбитраж-бота
    if stats_all.total_buys_and_sales_count > 0:
        if (
            stats_all.total_swaps_from_arbitrage_swap_events
            / stats_all.total_buys_and_sales_count
            >= 0.5
        ):
            return True
    # Токенов >= N и среднее время покупки-продажи <= X секунд
    if stats_all.total_token >= 500:
        if (duration := stats_all.token_buy_sell_duration_avg) and duration <= 2:
            return True
    if stats_all.total_token >= 1000:
        # Токенов >= N и средняя сумма покупки менее X
        if (avg_buy_amount := stats_all.token_avg_buy_amount) and avg_buy_amount < 30:
            return True
        # Токенов >= N и соотнешение "всего транзакций / всего токенов" > X
        if stats_all.total_buys_and_sales_count / stats_all.total_token > 10:
            return True

    return False


def determine_scammer_status(
    wallet: Wallet,
) -> bool:
    """Определяем статус скамера"""
    stats_all: WalletStatisticAll | None = wallet.stats_all
    # Если у кошелька более 5 токенов и процент "с продажей без покупки" больше N - помечаем как скамера
    if (
        stats_all.total_token >= 5
        and stats_all.token_sell_without_buy / stats_all.total_token >= 0.21
    ):
        return True
    # Если у кошелька более 5 токенов и процент продано>куплено больше N - помечаем как скамера
    if (
        stats_all.total_token >= 5
        and stats_all.token_with_sell_amount_gt_buy_amount / stats_all.total_token
        >= 0.21
    ):
        return True
    # Если у кошелька более 1 акктивности с 3+ трейдерами в одной транзе - помечаем его как скамера
    if stats_all.total_swaps_from_txs_with_mt_3_swappers > 0:
        return True

    return False


def filter_period_tokens(all_tokens, period, current_datetime) -> list:
    """Фильтруем только те токены у которых первая покупка попадает в диапазон и до нее нет продаж"""
    if period == 0:
        return all_tokens
    days = int(period)
    threshold_date = current_datetime - timedelta(days=days)

    period_tokens = []
    for token in all_tokens:
        fb_datetime = token.first_buy_timestamp
        fs_datetime = token.first_sell_timestamp
        if (fb_datetime and fb_datetime >= threshold_date) and (
            fs_datetime is None or fs_datetime >= threshold_date
        ):
            period_tokens.append(token)
        elif fs_datetime and fs_datetime >= threshold_date:
            period_tokens.append(token)

    return period_tokens


def recalculate_wallet_period_stats(stats, token_stats):
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

        total_swaps_from_txs_with_mt_3_swappers += (
            token.total_swaps_from_txs_with_mt_3_swappers
        )
        total_swaps_from_arbitrage_swap_events += (
            token.total_swaps_from_arbitrage_swap_events
        )

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
    stats.total_swaps_from_txs_with_mt_3_swappers = (
        total_swaps_from_txs_with_mt_3_swappers
    )
    stats.total_swaps_from_arbitrage_swap_events = (
        total_swaps_from_arbitrage_swap_events
    )

    stats.total_profit_multiplier = (
        stats.total_profit_usd / stats.total_token_buy_amount_usd * 100
        if stats.total_token_buy_amount_usd
        else None
    )  # Только для токенов у которых была покупка!

    stats.token_avg_buy_amount = (
        stats.total_token_buy_amount_usd / stats.token_with_buy
        if stats.token_with_buy
        else None
    )

    stats.token_first_buy_avg_price_usd = (
        sum(token_first_buy_price_values) / stats.token_with_buy
        if stats.token_with_buy
        else None
    )

    stats.token_first_buy_median_price_usd = (
        statistics.median(token_first_buy_price_values)
        if token_first_buy_price_values
        else None
    )

    stats.token_avg_profit_usd = (
        stats.total_profit_usd / stats.token_with_buy if stats.token_with_buy else None
    )  # Только для токенов у которых была покупка!

    stats.winrate = (
        profitable_tokens_count / stats.token_with_buy * 100
        if stats.token_with_buy
        else None
    )  # Только для токенов у которых была покупка!

    stats.token_buy_sell_duration_avg = (
        sum(token_first_buy_sell_duration_values) / stats.token_with_buy_and_sell
        if stats.token_with_buy_and_sell
        else None
    )

    stats.token_buy_sell_duration_median = (
        statistics.median(token_first_buy_sell_duration_values)
        if token_first_buy_sell_duration_values
        else None
    )

    stats.token_median_buy_amount = (
        statistics.median(token_buy_amount_usd_values)
        if token_buy_amount_usd_values
        else None
    )

    if stats.token_with_buy:
        stats.pnl_lt_minus_dot5_percent = (
            stats.pnl_lt_minus_dot5_num / stats.token_with_buy * 100
        )
        stats.pnl_minus_dot5_0x_percent = (
            stats.pnl_minus_dot5_0x_num / stats.token_with_buy * 100
        )
        stats.pnl_lt_2x_percent = stats.pnl_lt_2x_num / stats.token_with_buy * 100
        stats.pnl_2x_5x_percent = stats.pnl_2x_5x_num / stats.token_with_buy * 100
        stats.pnl_gt_5x_percent = stats.pnl_gt_5x_num / stats.token_with_buy * 100

    stats.updated_at = datetime.now(timezone.utc)
    return stats
