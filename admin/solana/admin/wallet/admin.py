from django.contrib import admin
from django.urls import path, reverse

from unfold.admin import ModelAdmin
from unfold.contrib.filters.admin import FieldTextFilter, RangeDateTimeFilter

from django.contrib.admin import DateFieldListFilter
from ...models import Wallet, WalletBase, WalletBuyPriceGt15k
from ..common.base_admin_model import BaseAdminModel
from ..common.misc import LargeTablePaginator
from .actions import WalletActionsMixin, WalletBuyPriceGt15kActionsMixin
from .displays import WalletDisplaysMixin, WalletStatsDisplaysMixin
from .filters import (GenericRangeFilter, IsBlacklistedFilter, IsBotFilter,
                      IsFavoriteFilter, IsScammerFilter, IsWatchLaterFilter,
                      PeriodFilter, TokensIntersectionFilter)
from .inlines import (WalletStatistic7dInline, WalletStatistic30dInline,
                      WalletStatisticAllInline, WalletTokenStatisticInline)
from .views import WalletStatisticBuyPriceGt15kView, WalletStatisticView

PERIODS = {"7d": "7 дней", "30d": "30 дней", "all": "Все время"}


def get_period_buttons(selected_period):
    buttons = []
    # Формируем список кнопок
    for period in PERIODS:
        active_class = "active" if period == selected_period else ""
        button = {
            "period": period,
            "active_class": active_class,
            "label": PERIODS[period].capitalize(),
        }
        buttons.append(button)

    return buttons


@admin.register(WalletBase)
class WalletBaseAdmin(WalletStatsDisplaysMixin, ModelAdmin):
    """Базовая админ-модель кошелька"""

    inlines = [
        WalletStatistic7dInline,
        WalletStatistic30dInline,
        WalletStatisticAllInline,
        WalletTokenStatisticInline,
    ]
    show_full_result_count = False
    paginator = LargeTablePaginator
    readonly_fields = (
        "last_stats_check",
        "created_at",
        "updated_at",
    )
    list_display = ("address", "last_stats_check")
    list_display_links = ("address",)
    search_fields = ("address__exact",)

    list_filter = [
        ("address", FieldTextFilter),
        ("last_stats_check", DateFieldListFilter),
        ("created_at", RangeDateTimeFilter),
    ]


@admin.register(Wallet)
class WalletAdmin(
    BaseAdminModel,
    WalletActionsMixin,
    WalletDisplaysMixin,
    WalletStatsDisplaysMixin,
):
    list_before_template = "admin/wallet/wallet_list_before.html"
    readonly_fields = ("created_at", "updated_at")
    search_fields = ("address__exact",)
    ordering = ["-created_at"]
    actions_row = ["open_stats", "open_gmgn", "open_cielo", "open_solscan"]
    actions = [
        "export_wallets_to_file",
        "add_wallets_to_favorites",
        "remove_wallets_from_favorites",
        "add_wallets_to_blacklist",
        "remove_wallets_from_blacklist",
        "add_wallets_to_watch_later",
        "remove_wallets_from_watch_later",
    ]

    def get_changelist_instance(self, request):
        cl = super().get_changelist_instance(request)
        cl.title = "Кошельки"
        return cl

    def changelist_view(self, request, extra_context=None):
        period = request.GET.get("period", "all")
        extra_context = extra_context or {}
        if period:
            extra_context["period_title_value"] = PERIODS[period]
            extra_context["selected_period"] = period
            extra_context["period_buttons"] = get_period_buttons(period)

        return super().changelist_view(request, extra_context=extra_context)

    def get_list_display(self, request):
        def get_displays_for_active_period(period=None) -> list[str]:
            base = [
                "wallet_display",
                "{stats_rel_name}__winrate_display",
                "stats_all__winrate_display",
                "{stats_rel_name}__total_profit_usd_display",
                "{stats_rel_name}__total_profit_multiplier_display",
                "{stats_rel_name}__pnl_gt_5x_display",
                "{stats_rel_name}__pnl_2x_5x_display",
                "{stats_rel_name}__pnl_lt_2x_display",
                "{stats_rel_name}__pnl_minus_dot5_0_display",
                "{stats_rel_name}__pnl_lt_minus_dot5_display",
                "{stats_rel_name}__total_token_display",
                "{stats_rel_name}__token_avg_buy_amount_display",
                "{stats_rel_name}__token_avg_profit_usd_display",
                "{stats_rel_name}__token_first_buy_median_price_usd_display",
                "{stats_rel_name}__token_buy_sell_duration_median_display",
                "last_update_display",
            ]

            if period == '7d':
                stats_rel_name = 'stats_7d'
            elif period == '30d':
                stats_rel_name = 'stats_30d'
            elif period == 'all':
                stats_rel_name = 'stats_all'
            else:
                return []
            return [item.format(stats_rel_name=stats_rel_name) if '{stats_rel_name}' in item else item for item in base]

        _period = request.GET.get("period", "all")

        return get_displays_for_active_period(_period)

    def get_list_filters_for_stats(self, prefix):
        """Формирует список фильтров по заданному префиксу."""
        return [
            (f"{prefix}__winrate", GenericRangeFilter),
            (f"{prefix}__total_profit_usd", GenericRangeFilter),
            (f"{prefix}__total_profit_multiplier", GenericRangeFilter),
            (f"{prefix}__total_token", GenericRangeFilter),
            (f"{prefix}__token_avg_buy_amount", GenericRangeFilter),
            (f"{prefix}__token_avg_profit_usd", GenericRangeFilter),
            (f"{prefix}__pnl_gt_5x_percent", GenericRangeFilter),
            (f"{prefix}__token_first_buy_median_price_usd", GenericRangeFilter),
            (f"{prefix}__token_buy_sell_duration_median", GenericRangeFilter),
        ]

    def get_list_filter(self, request):
        return (
                self.get_list_filters_for_stats("stats_all")
                + self.get_list_filters_for_stats("stats_7d")
                + self.get_list_filters_for_stats("stats_30d")
                + [
                    TokensIntersectionFilter,
                    IsFavoriteFilter,
                    IsWatchLaterFilter,
                    IsBlacklistedFilter,
                    IsScammerFilter,
                    IsBotFilter,
                    PeriodFilter,
                ]
        )

    def get_urls(self):
        return [
            path("<str:wallet_address>/", WalletStatisticView.as_view(model_admin=self), name="wallet_statistic_view"),
        ] + super().get_urls()


@admin.register(WalletBuyPriceGt15k)
class WalletBuyPriceGt15kAdmin(
    BaseAdminModel,
    WalletBuyPriceGt15kActionsMixin,
    WalletDisplaysMixin,
    WalletStatsDisplaysMixin,
):
    list_before_template = "admin/wallet/wallet_list_before.html"
    readonly_fields = ("created_at", "updated_at")
    search_fields = ("address__exact",)
    ordering = ["-created_at"]
    actions_row = ["open_stats", "open_gmgn", "open_cielo", "open_solscan"]

    actions = [
        "export_wallets_to_file",
        "add_wallets_to_favorites",
        "remove_wallets_from_favorites",
        "add_wallets_to_blacklist",
        "remove_wallets_from_blacklist",
        "add_wallets_to_watch_later",
        "remove_wallets_from_watch_later",
    ]

    def get_urls(self):
        return [
            path("<str:wallet_address>/", WalletStatisticBuyPriceGt15kView.as_view(model_admin=self), name="wallet_statistic_view"),
        ] + super().get_urls()

    def get_changelist_instance(self, request):
        cl = super().get_changelist_instance(request)
        cl.title = "Кошельки"
        return cl

    def get_queryset(self, request):
        return super().get_queryset(request).filter(
            stats_buy_price_gt_15k_7d__isnull=False,
            stats_buy_price_gt_15k_30d__isnull=False,
            stats_buy_price_gt_15k_all__isnull=False,
        )

    def changelist_view(self, request, extra_context=None):
        period = request.GET.get("period", "all")
        # Дополняем контекст, если фильтр активен
        extra_context = extra_context or {}
        if period:
            extra_context["period_title_value"] = PERIODS[period]
            extra_context["selected_period"] = period
            extra_context["period_buttons"] = get_period_buttons(period)

        return super().changelist_view(request, extra_context=extra_context)

    def get_list_display(self, request):
        def get_displays_for_active_period(period=None) -> list[str]:
            base = [
                "wallet_display",
                "{stats_rel_name}__winrate_display",
                "stats_buy_price_gt_15k_all__winrate_display",
                "{stats_rel_name}__total_profit_usd_display",
                "{stats_rel_name}__total_profit_multiplier_display",
                "{stats_rel_name}__pnl_gt_5x_display",
                "{stats_rel_name}__pnl_2x_5x_display",
                "{stats_rel_name}__pnl_lt_2x_display",
                "{stats_rel_name}__pnl_minus_dot5_0_display",
                "{stats_rel_name}__pnl_lt_minus_dot5_display",
                "{stats_rel_name}__total_token_display",
                "{stats_rel_name}__token_avg_buy_amount_display",
                "{stats_rel_name}__token_avg_profit_usd_display",
                "{stats_rel_name}__token_first_buy_median_price_usd_display",
                "{stats_rel_name}__token_buy_sell_duration_median_display",
                "last_update_display",
            ]

            if period == '7d':
                stats_rel_name = 'stats_buy_price_gt_15k_7d'
            elif period == '30d':
                stats_rel_name = 'stats_buy_price_gt_15k_30d'
            elif period == 'all':
                stats_rel_name = 'stats_buy_price_gt_15k_all'
            else:
                return []
            return [item.format(stats_rel_name=stats_rel_name) if '{stats_rel_name}' in item else item for item in base]

        _period = request.GET.get("period", "all")

        return get_displays_for_active_period(_period)

    def get_list_filters_for_stats(self, prefix):
        """Формирует список фильтров по заданному префиксу."""
        return [
            (f"{prefix}__winrate", GenericRangeFilter),
            (f"{prefix}__total_profit_usd", GenericRangeFilter),
            (f"{prefix}__total_profit_multiplier", GenericRangeFilter),
            (f"{prefix}__total_token", GenericRangeFilter),
            (f"{prefix}__token_avg_buy_amount", GenericRangeFilter),
            (f"{prefix}__token_avg_profit_usd", GenericRangeFilter),
            (f"{prefix}__pnl_gt_5x_percent", GenericRangeFilter),
            (f"{prefix}__token_first_buy_median_price_usd", GenericRangeFilter),
            (f"{prefix}__token_buy_sell_duration_median", GenericRangeFilter),
        ]

    def get_list_filter(self, request):
        return (
            self.get_list_filters_for_stats("stats_buy_price_gt_15k_all")
            + self.get_list_filters_for_stats("stats_buy_price_gt_15k_7d")
            + self.get_list_filters_for_stats("stats_buy_price_gt_15k_30d")
            + [
                TokensIntersectionFilter,
                IsFavoriteFilter,
                IsWatchLaterFilter,
                IsBlacklistedFilter,
                IsScammerFilter,
                IsBotFilter,
                PeriodFilter,
            ]
        )





