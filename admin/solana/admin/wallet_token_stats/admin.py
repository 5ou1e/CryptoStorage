from django.contrib import admin
from unfold.contrib.filters.admin import FieldTextFilter, RangeNumericFilter

from solana.models import WalletTokenStatistic

from ..shared.base_admin_model import BaseAdminModel
from ..shared.filters import TokenAddressFilter, WalletAddressFilter
from .displays import WalletTokenDisplays
from .filters import IsTokenSellAmountGtBuyAmountFilter


@admin.register(WalletTokenStatistic)
class WalletTokenStatisticAdmin(BaseAdminModel):
    autocomplete_fields = ["token", "wallet"]
    list_display = [
        "token__symbol",
        "token__address",
        "wallet__address",
        "created_at",
        "updated_at",
    ]
    list_display_links = [
        "token__symbol",
        "token__address",
        "wallet__address",
    ]
    search_fields = [
        "token__address__exact",
        "wallet__address__exact",
    ]
    list_filter = [WalletAddressFilter, TokenAddressFilter]


class WalletTokenStatisticForWalletStatsPageAdmin(
    WalletTokenDisplays, WalletTokenStatisticAdmin
):
    """ Админ-модель для таблицы кошелек-токен на странице статистики кошелька"""

    actions = None
    list_editable = ()
    ordering = ["-last_activity_timestamp"]
    search_fields = ["token__name", "token__address", "wallet__address"]
    list_display = [
        "token_name_display",
        "total_buy_amount_usd_display",
        "total_sell_amount_usd_display",
        "total_profit_usd_display",
        "total_profit_percent_display",
        "total_buys_count_display",
        "total_sales_count_display",
        "first_buy_sell_duration_display",
        "first_buy_price_usd_display",
        "first_sell_price_usd_display",
        "first_buy_timestamp_display",
        "first_sell_timestamp_display",
        "actions_display",
    ]
    list_filter = [
        ("token__name", FieldTextFilter),
        ("token__address", FieldTextFilter),
        ("total_profit_usd", RangeNumericFilter),
        ("total_profit_percent", RangeNumericFilter),
        ("total_buys_count", RangeNumericFilter),
        ("total_sales_count", RangeNumericFilter),
        ("first_buy_sell_duration", RangeNumericFilter),
        ("first_buy_price_usd", RangeNumericFilter),
        ("first_sell_price_usd", RangeNumericFilter),
        ("total_swaps_from_txs_with_mt_3_swappers", RangeNumericFilter),
        ("total_swaps_from_arbitrage_swap_events", RangeNumericFilter),
        IsTokenSellAmountGtBuyAmountFilter,
    ]

    @staticmethod
    def _url_for_result(self, result):
        return "#"

    def has_change_permission(*args, **kwargs):
        """ Отключаем возможность изменений (возможно это не работает как ожидается) """
        return False
