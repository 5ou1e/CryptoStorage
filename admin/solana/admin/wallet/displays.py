from django.template.loader import render_to_string
from django.utils.html import mark_safe
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from unfold.decorators import display

from solana.models import Wallet
from utils.number_utils import formatted_number, round_to_first_non_zero
from utils.time_utils import format_duration

PERIODS = {"7d": "7 дней", "30d": "30 дней", "all": "Все время"}

DISPLAY_LABELS = {
    "good": "success",
    "warning": "warning",
    "bad": "danger",
    "ok": "default",
}


class WalletDisplaysMixin:
    @display(
        description=_("Адрес"),
        ordering="-address",
    )
    def wallet_display(self, obj: Wallet):
        copy_button = render_to_string(
            "admin/copy_button.html",
            {
                "copy_value": obj.address,
            },  # передаем нужные данные в контекст
        )
        value = f"""
                    <div class="flex gap-1 font-semibold text-font-default-light dark:text-font-default-dark">
                        <a href="{obj.get_stats_url()} " title="{obj.address}" target="_blank">{obj.address[:5]}...{obj.address[-2:]}</a>
                        <span class="text-font-subtle-light dark:text-font-subtle-dark">{copy_button}</span>
                    </div>
                """
        return mark_safe(value)

    @display(
        description=_("Обн"),
        ordering="-last_stats_check",
    )
    def last_update_display(self, obj):
        last_stats_update_title = obj.last_stats_check
        last_stats_update_value = (
            format_duration(now() - obj.last_stats_check) + " наз."
            if obj.last_stats_check
            else "-"
        )
        value = f"""
                <div>
                    <p class="text-base " title="{ last_stats_update_title }" class="text-base text-sm text-font-subtle-light dark:text-font-subtle-dark">{ last_stats_update_value }</p>
                </div>
                """
        return mark_safe(value)

    # @display(
    #     description=_("Баланс"),
    #     ordering="-sol_balance",
    # )
    # def sol_balance_display(self, obj):
    #     value = round_to_first_non_zero(obj.details.sol_balance)
    #     return f"{value} SOL" if value else "0.00 SOL"


class WalletStatsDisplayMethods:
    """
    Display функции статистик
    """

    @classmethod
    def winrate_display(cls, obj):
        if obj.winrate is None:
            return None
        value = round(obj.winrate, 2)
        return "good" if value >= 50 else "bad", f"{value} %"

    @classmethod
    def total_profit_usd_display(cls, obj):
        if obj.total_profit_usd is None:
            return None
        return formatted_number(obj.total_profit_usd, suffix=" $", add_sign=True)

    @classmethod
    def total_profit_multiplier_display(cls, obj):
        if obj.total_profit_multiplier is None:
            return None
        value = obj.total_profit_multiplier
        return (
            "good" if value >= 1 else "ok" if value >= 0 else "bad",
            formatted_number(value, suffix=" %", add_sign=True),
        )

    @classmethod
    def total_token_display(cls, obj):
        return None if not obj else obj.total_token

    @classmethod
    def pnl_display(cls, obj, attr, label):
        if not obj:
            return None
        value = getattr(obj, attr, None)
        return label, formatted_number(value, decimals=1, zero_value="-", suffix=" %")

    @classmethod
    def pnl_lt_minus_dot5_display(cls, obj):
        return cls.pnl_display(obj, "pnl_lt_minus_dot5_percent", "bad")

    @classmethod
    def pnl_minus_dot5_0_display(cls, obj):
        return cls.pnl_display(obj, "pnl_minus_dot5_0x_percent", "bad")

    @classmethod
    def pnl_lt_2x_display(cls, obj):
        return cls.pnl_display(obj, "pnl_lt_2x_percent", "good")

    @classmethod
    def pnl_2x_5x_display(cls, obj):
        return cls.pnl_display(obj, "pnl_2x_5x_percent", "good")

    @classmethod
    def pnl_gt_5x_display(cls, obj):
        return cls.pnl_display(obj, "pnl_gt_5x_percent", "good")

    @classmethod
    def token_avg_buy_amount_display(cls, obj):
        return (
            None
            if not obj or obj.token_avg_buy_amount is None
            else formatted_number(obj.token_avg_buy_amount, suffix=" $")
        )

    @classmethod
    def token_buy_sell_duration_median_display(cls, obj):
        if not obj or obj.token_buy_sell_duration_median is None:
            return None
        value = obj.token_buy_sell_duration_median
        label = "ok" if value > 30 else "warning" if value > 5 else "bad"
        return label, format_duration(value)

    @classmethod
    def token_avg_profit_usd_display(cls, obj):
        return (
            None
            if not obj or obj.token_avg_profit_usd is None
            else formatted_number(obj.token_avg_profit_usd, suffix=" $", add_sign=True)
        )

    @classmethod
    def token_first_buy_median_price_usd_display(cls, obj):
        return (
            None
            if not obj or obj.token_first_buy_median_price_usd is None
            else formatted_number(
                obj.token_first_buy_median_price_usd,
                decimals=10,
                suffix=" $",
                subscript=True,
            )
        )


class WalletStatsDisplaysConfigurator:
    STAT_PERIODS = {
        "7": "stats_7d",
        "30": "stats_30d",
        "Все": "stats_all",
        "_7": "stats_buy_price_gt_15k_7d",
        "_30": "stats_buy_price_gt_15k_30d",
        "_Все": "stats_buy_price_gt_15k_all",
    }

    BASE_METHODS_DISPLAY_META = {
        "winrate_display": {
            "description": _("В/Р"),
            "ordering": "-{related_name}__winrate",
            "label": DISPLAY_LABELS,
        },
        "total_profit_usd_display": {
            "description": _("Профит $"),
            "ordering": "-{related_name}__total_profit_usd",
        },
        "total_profit_multiplier_display": {
            "description": _("Профит %"),
            "ordering": "-{related_name}__total_profit_multiplier",
            "label": DISPLAY_LABELS,
        },
        "total_token_display": {
            "description": _("Токенов"),
            "ordering": "-{related_name}__total_token",
        },
        "pnl_lt_minus_dot5_display": {
            "description": _("< 0.5x"),
            "ordering": "-{related_name}__pnl_lt_minus_dot5_percent",
            "label": DISPLAY_LABELS,
        },
        "pnl_minus_dot5_0_display": {
            "description": _("0 - -0.5x"),
            "ordering": "-{related_name}__pnl_minus_dot5_0x_percent",
            "label": DISPLAY_LABELS,
        },
        "pnl_lt_2x_display": {
            "description": _("0x - 2x"),
            "ordering": "-{related_name}__pnl_lt_2x_percent",
            "label": DISPLAY_LABELS,
        },
        "pnl_2x_5x_display": {
            "description": _("2x - 5x"),
            "ordering": "-{related_name}__pnl_2x_5x_percent",
            "label": DISPLAY_LABELS,
        },
        "pnl_gt_5x_display": {
            "description": _(">5x"),
            "ordering": "-{related_name}__pnl_gt_5x_percent",
            "label": DISPLAY_LABELS,
        },
        "token_avg_buy_amount_display": {
            "description": _("Ср. пок."),
            "ordering": "-{related_name}__token_avg_buy_amount",
        },
        "token_buy_sell_duration_median_display": {
            "description": _("Холд"),
            "ordering": "-{related_name}__token_buy_sell_duration_median",
            "label": DISPLAY_LABELS,
        },
        "token_avg_profit_usd_display": {
            "description": _("Ср. профит"),
            "ordering": "-{related_name}__token_avg_profit_usd",
        },
        "token_first_buy_median_price_usd_display": {
            "description": _("Сред ц.1п"),
            "ordering": "-{related_name}__token_first_buy_median_price_usd",
        },
    }

    @classmethod
    def generate_methods(cls):
        """
        Динамически создаёт методы для всех таблиц статистики.
        """
        result_methods = {}
        for period, related_name in cls.STAT_PERIODS.items():
            for method_name, meta in cls.BASE_METHODS_DISPLAY_META.items():
                new_method_name = f"{related_name}__{method_name}"

                def method(
                    self, obj, method_name=method_name, related_name=related_name
                ):
                    # Если это статистика, используем её напрямую
                    if hasattr(obj, related_name):
                        related_obj = getattr(obj, related_name, None)
                    else:
                        related_obj = obj  # Объект статистики напрямую

                    func = getattr(WalletStatsDisplayMethods, method_name)
                    return func(related_obj)

                description = f"{meta['description']}"
                if period in ["Все", "_Все"] and method_name == "winrate_display":
                    description += " Все"

                method = display(
                    description=description,  # ({period})
                    ordering=meta["ordering"].format(related_name=related_name),
                    label=meta.get("label"),
                )(method)
                method.__name__ = new_method_name
                result_methods[new_method_name] = method

        return result_methods

    def configure_displays(cls):
        extra_methods = WalletStatsDisplaysConfigurator.generate_methods()
        for name, method in extra_methods.items():
            setattr(cls, name, method)
        return cls


@WalletStatsDisplaysConfigurator.configure_displays
class WalletStatsDisplaysMixin:
    pass
