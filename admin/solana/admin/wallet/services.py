from datetime import timedelta

from django.utils.timezone import now

from users.models import UserWallet
from utils.number_utils import formatted_number as f_n
from utils.time_utils import formatted_duration as f_d


def get_wallet_statistics_data(user, wallet, use_buy_price_gt_20k_stats=False):
    user_wallet = UserWallet.objects.filter(user=user, wallet=wallet).first()

    remark = user_wallet.remark if user_wallet else None
    details = getattr(wallet, "details", None)
    data = dict()
    data["wallet_id"] = wallet.pk
    data["favorite"] = user_wallet.is_favorite if user_wallet else False
    data["blacklisted"] = user_wallet.is_blacklisted if user_wallet else False
    data["watch_later"] = user_wallet.is_watch_later if user_wallet else False
    data["remark"] = remark or ""
    data["address"] = wallet.address
    data["sol_balance"] = f_n(details.sol_balance if details else None, suffix=" SOL")
    data["last_stats_updated_time_ago"] = {
        "display_value": (
            f_d(now() - wallet.last_stats_check) + " назад"
            if wallet.last_stats_check
            else "-"
        ),
        "value": wallet.last_stats_check,
    }

    periods_data = {
        "7d": {},
        "30d": {},
        "all": {},
    }
    for period in periods_data:
        period_data = periods_data[period]
        if period == "7d":
            if use_buy_price_gt_20k_stats:
                period_stats = wallet.stats_buy_price_gt_15k_7d
            else:
                period_stats = getattr(wallet, "stats_7d", None)
        elif period == "30d":
            if use_buy_price_gt_20k_stats:
                period_stats = wallet.stats_buy_price_gt_15k_30d
            else:
                period_stats = getattr(wallet, "stats_30d", None)
        else:
            if use_buy_price_gt_20k_stats:
                period_stats = wallet.stats_buy_price_gt_15k_all
            else:
                period_stats = getattr(wallet, "stats_all", None)
        if not period_stats:
            continue

        period_data["winrate"] = {
            "display_value": (
                f_n(period_stats.winrate, suffix=" %")
                if period_stats.winrate is not None
                else "-"
            ),
            "value": period_stats.winrate,
        }
        period_data["total_profit"] = {
            "display_value": f_n(
                period_stats.total_profit_usd, suffix=" $", add_sign=True
            ),
            "value": period_stats.total_profit_usd,
        }
        period_data["total_profit_multiplier"] = {
            "display_value": f_n(
                period_stats.total_profit_multiplier, suffix=" %", add_sign=True
            ),
            "value": period_stats.total_profit_multiplier,
        }
        period_data["total_token"] = f_n(period_stats.total_token)
        if period_stats.token_sell_without_buy is not None and period_stats.total_token:
            token_sell_without_buy_percent = (
                period_stats.token_sell_without_buy / period_stats.total_token * 100
            )
        else:
            token_sell_without_buy_percent = None
        period_data["token_sell_without_buy"] = {
            "display_value": f"{f_n(period_stats.token_sell_without_buy)} ({f_n(token_sell_without_buy_percent, decimals=1, suffix='%')})",
        }
        if period_stats.token_buy_without_sell is not None and period_stats.total_token:
            token_buy_without_sell_percent = (
                period_stats.token_buy_without_sell / period_stats.total_token * 100
            )
        else:
            token_buy_without_sell_percent = None
        period_data["token_buy_without_sell"] = {
            "display_value": f"{f_n(period_stats.token_buy_without_sell)} ({f_n(token_buy_without_sell_percent, decimals=1, suffix='%')})",
        }

        if (
            period_stats.token_with_sell_amount_gt_buy_amount is not None
            and period_stats.total_token
        ):
            token_with_sell_amount_gt_buy_amount_percent = (
                period_stats.token_with_sell_amount_gt_buy_amount
                / period_stats.total_token
                * 100
            )
        else:
            token_with_sell_amount_gt_buy_amount_percent = None
        period_data["token_with_sell_amount_gt_buy_amount"] = {
            "display_value": f"{f_n(period_stats.token_with_sell_amount_gt_buy_amount)} ({f_n(token_with_sell_amount_gt_buy_amount_percent, decimals=1, suffix='%')})",
        }
        total_token_transactions = (
            period_stats.total_token_buys + period_stats.total_token_sales
            if (
                period_stats.total_token_buys is not None
                and period_stats.total_token_sales is not None
            )
            else None
        )
        period_data["total_token_transactions"] = f_n(total_token_transactions)
        period_data["total_token_buys"] = f_n(period_stats.total_token_buys)
        period_data["total_token_sales"] = f_n(period_stats.total_token_sales)

        period_data["total_token_buy_amount_usd"] = {
            "display_value": f_n(period_stats.total_token_buy_amount_usd, suffix=" $")
        }
        period_data["total_token_sell_amount_usd"] = {
            "display_value": f_n(period_stats.total_token_sell_amount_usd, suffix=" $")
        }

        period_data["token_avg_profit_usd"] = {
            "display_value": f_n(period_stats.token_avg_profit_usd, suffix=" $"),
            "value": period_stats.token_avg_profit_usd,
        }

        period_data["token_avg_buy_amount"] = f_n(
            period_stats.token_avg_buy_amount, suffix=" $"
        )
        period_data["token_median_buy_amount"] = {
            "display_value": f_n(period_stats.token_median_buy_amount, suffix=" $"),
        }
        period_data["token_buy_sell_duration_avg"] = {
            "display_value": (
                f_d(int(period_stats.token_buy_sell_duration_avg))
                if period_stats.token_buy_sell_duration_avg
                else None
            ),
            "value": (
                timedelta(seconds=int(period_stats.token_buy_sell_duration_avg))
                if period_stats.token_buy_sell_duration_avg
                else None
            ),
        }
        period_data["token_buy_sell_duration_median"] = {
            "display_value": f_d(period_stats.token_buy_sell_duration_median),
            "value": period_stats.token_buy_sell_duration_median,
        }
        period_data["token_first_buy_avg_price_usd"] = {
            "display_value": f_n(
                period_stats.token_first_buy_avg_price_usd,
                suffix=" $",
                decimals=10,
                subscript=True,
            ),
            "value": period_stats.token_first_buy_avg_price_usd,
        }
        period_data["token_first_buy_median_price_usd"] = {
            "display_value": f_n(
                period_stats.token_first_buy_median_price_usd,
                suffix=" $",
                decimals=10,
                subscript=True,
            ),
            "value": period_stats.token_first_buy_median_price_usd,
        }

        period_data["pnl_gt_5x_num"] = (
            f"{f_n(period_stats.pnl_gt_5x_num)} ({f_n(period_stats.pnl_gt_5x_percent, suffix=' %')})"
        )
        period_data["pnl_2x_5x_num"] = (
            f"{f_n(period_stats.pnl_2x_5x_num)} ({f_n(period_stats.pnl_2x_5x_percent, suffix=' %')})"
        )
        period_data["pnl_lt_2x_num"] = (
            f"{f_n(period_stats.pnl_lt_2x_num)} ({f_n(period_stats.pnl_lt_2x_percent, suffix=' %')})"
        )
        period_data["pnl_minus_dot5_0x_num"] = (
            f"{f_n(period_stats.pnl_minus_dot5_0x_num)} ({f_n(period_stats.pnl_minus_dot5_0x_percent, suffix=' %')})"
        )
        period_data["pnl_lt_minus_dot5_num"] = (
            f"{f_n(period_stats.pnl_lt_minus_dot5_num)} ({f_n(period_stats.pnl_lt_minus_dot5_percent, suffix=' %')})"
        )

    data["periods_data"] = periods_data

    return data
