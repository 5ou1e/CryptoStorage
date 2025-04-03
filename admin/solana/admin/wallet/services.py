from datetime import timedelta

from django.utils.timezone import now

from users.models import UserWallet
from utils.number_utils import formatted_number as f_n
from utils.time_utils import format_duration as f_d


def get_wallet_statistics_data(user, wallet, use_buy_price_gt_20k_stats=False):
    user_wallet = UserWallet.objects.filter(user=user, wallet=wallet).first()

    remark = user_wallet.remark if user_wallet else None
    details = getattr(wallet, "details", None)
    data = {
        "wallet_id": wallet.pk,
        "favorite": user_wallet.is_favorite if user_wallet else False,
        "blacklisted": user_wallet.is_blacklisted if user_wallet else False,
        "watch_later": user_wallet.is_watch_later if user_wallet else False,
        "remark": remark or "",
        "address": wallet.address,
        "sol_balance": f_n(details.sol_balance if details else None, suffix=" SOL"),
        "last_stats_updated_time_ago": {
            "display_value": (
                f_d(now() - wallet.last_stats_check) + " назад"
                if wallet.last_stats_check
                else "-"
            ),
            "value": wallet.last_stats_check,
        },
    }

    periods_data = {period: {} for period in ["7d", "30d", "all"]}

    for period in periods_data:
        period_data = periods_data[period]

        period_stats = getattr(
            wallet,
            (
                f"stats_buy_price_gt_15k_{period}"
                if use_buy_price_gt_20k_stats
                else f"stats_{period}"
            ),
            None,
        )
        if not period_stats:
            continue

        period_data.update(
            {
                "winrate": {
                    "display_value": (
                        f_n(period_stats.winrate, suffix=" %")
                        if period_stats.winrate is not None
                        else "-"
                    ),
                    "value": period_stats.winrate,
                },
                "total_profit": {
                    "display_value": f_n(
                        period_stats.total_profit_usd, suffix=" $", add_sign=True
                    ),
                    "value": period_stats.total_profit_usd,
                },
                "total_profit_multiplier": {
                    "display_value": f_n(
                        period_stats.total_profit_multiplier, suffix=" %", add_sign=True
                    ),
                    "value": period_stats.total_profit_multiplier,
                },
                "total_token": f_n(period_stats.total_token),
                "total_token_transactions": f_n(
                    period_stats.total_token_buys + period_stats.total_token_sales
                    if period_stats.total_token_buys is not None
                    and period_stats.total_token_sales is not None
                    else None
                ),
                "total_token_buys": f_n(period_stats.total_token_buys),
                "total_token_sales": f_n(period_stats.total_token_sales),
                "total_token_buy_amount_usd": {
                    "display_value": f_n(
                        period_stats.total_token_buy_amount_usd, suffix=" $"
                    )
                },
                "total_token_sell_amount_usd": {
                    "display_value": f_n(
                        period_stats.total_token_sell_amount_usd, suffix=" $"
                    )
                },
                "token_avg_profit_usd": {
                    "display_value": f_n(
                        period_stats.token_avg_profit_usd, suffix=" $"
                    ),
                    "value": period_stats.token_avg_profit_usd,
                },
                "token_avg_buy_amount": f_n(
                    period_stats.token_avg_buy_amount, suffix=" $"
                ),
                "token_median_buy_amount": {
                    "display_value": f_n(
                        period_stats.token_median_buy_amount, suffix=" $"
                    ),
                },
                "token_first_buy_avg_price_usd": {
                    "display_value": f_n(
                        period_stats.token_first_buy_avg_price_usd,
                        suffix=" $",
                        decimals=10,
                        subscript=True,
                    ),
                    "value": period_stats.token_first_buy_avg_price_usd,
                },
                "token_first_buy_median_price_usd": {
                    "display_value": f_n(
                        period_stats.token_first_buy_median_price_usd,
                        suffix=" $",
                        decimals=10,
                        subscript=True,
                    ),
                    "value": period_stats.token_first_buy_median_price_usd,
                },
            }
        )

        for key in [
            "token_sell_without_buy",
            "token_buy_without_sell",
            "token_with_sell_amount_gt_buy_amount",
        ]:
            total = period_stats.total_token
            value = getattr(period_stats, key, None)
            percent = (
                f_n(value / total * 100, decimals=1, suffix="%")
                if value is not None and total
                else "-"
            )
            period_data[key] = {"display_value": f"{f_n(value)} ({percent})"}

        for key in [
            "pnl_gt_5x",
            "pnl_2x_5x",
            "pnl_lt_2x",
            "pnl_minus_dot5_0x",
            "pnl_lt_minus_dot5",
        ]:
            num = getattr(period_stats, f"{key}_num", None)
            percent = getattr(period_stats, f"{key}_percent", None)
            period_data[key] = f"{f_n(num)} ({f_n(percent, suffix=' %')})"

        # Исправленная обработка token_buy_sell_duration_avg
        token_duration_avg = period_stats.token_buy_sell_duration_avg
        period_data["token_buy_sell_duration_avg"] = {
            "display_value": (
                f_d(token_duration_avg) if token_duration_avg is not None else None
            ),
            "value": (
                timedelta(seconds=token_duration_avg)
                if token_duration_avg is not None
                else None
            ),
        }

        period_data["token_buy_sell_duration_median"] = {
            "display_value": f_d(period_stats.token_buy_sell_duration_median),
            "value": period_stats.token_buy_sell_duration_median,
        }

    data["periods_data"] = periods_data
    return data
