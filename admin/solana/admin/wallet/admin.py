from django.contrib import admin
from django.http import HttpRequest, HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import path, reverse
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin
from unfold.contrib.filters.admin import FieldTextFilter, RangeDateTimeFilter
from unfold.decorators import action, display

from ...models import (Wallet, WalletBuyPriceGt15k, WalletProxy,
                       WalletStatistic7d, WalletStatistic30d,
                       WalletStatisticAll, WalletTokenStatistic)
from ..shared.base_admin_model import BaseAdminModel
from ..shared.misc import LargeTablePaginator
from .actions import WalletActions
from .displays import (WalletDisplays, WalletStatsDisplays,
                       WalletStatsDisplaysConfigurator)
from .filters import (CustomRangeFilter, IsBlacklistedFilter, IsBotFilter,
                      IsFavoriteFilter, IsScammerFilter, IsWatchLaterFilter,
                      PeriodFilter, TokensIntersectionFilter)
from .inlines import (WalletStatistic7dInline, WalletStatistic30dInline,
                      WalletStatisticAllInline, WalletTokenStatisticInline)
from .views import WalletStatisticBuyPriceGt15kView, WalletStatisticView

PERIODS = {"7d": "7 дней", "30d": "30 дней", "all": "Все время"}

DISPLAY_LABELS = {
    "good": "success",
    "warning": "warning",
    "bad": "danger",
    "ok": "default",
}


@admin.register(WalletProxy)
class WalletProxyAdmin(WalletStatsDisplays, ModelAdmin):
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
    list_filter_submit = True  # Submit button at the bottom of the filter
    from django.contrib.admin import DateFieldListFilter

    list_filter = [
        ("address", FieldTextFilter),
        ("last_stats_check", DateFieldListFilter),
        ("created_at", RangeDateTimeFilter),
    ]


from unfold.sections import TableSection


class WalletStats7dTableSection(TableSection, WalletStatsDisplays):
    verbose_name = _("Статистика за 7 дней")  # Displays custom table title
    height = 300  # Force the table height. Ideal for large amount of records
    related_name = "stats_7d"  # Related model field name
    fields = [
        field.name for field in WalletStatistic7d._meta.fields
    ]  # Fields from related model


class WalletStats30dTableSection(TableSection):
    verbose_name = _("Статистика за 30 дней")  # Displays custom table title
    height = 300  # Force the table height. Ideal for large amount of records
    related_name = "stats_30d"  # Related model field name
    fields = [
        field.name for field in WalletStatistic30d._meta.fields
    ]  # Fields from related model


class WalletStatsAllTableSection(TableSection):
    verbose_name = _("Статистика за все время")  # Displays custom table title
    height = 300  # Force the table height. Ideal for large amount of records
    related_name = "stats_all"  # Related model field name
    fields = [
        field.name for field in WalletStatisticAll._meta.fields
    ]  # Fields from related model


@admin.register(Wallet)
class WalletAdmin(
    BaseAdminModel,
    WalletDisplays,
    WalletActions,
    WalletStatsDisplays,
):
    list_before_template = "admin/wallet/wallet_list_before.html"
    inlines = []
    list_sections = [
        WalletStats7dTableSection,
        WalletStats30dTableSection,
        WalletStatsAllTableSection,
    ]
    readonly_fields = (
        "created_at",
        "updated_at",
    )
    search_fields = ("address__exact",)
    ordering = ["-created_at"]

    def get_list_filter(self, request):
        return [
            # ("details__sol_balance", CustomRangeFilter),
            ("stats_all__winrate", CustomRangeFilter),
            ("stats_all__total_profit_usd", CustomRangeFilter),
            ("stats_all__total_profit_multiplier", CustomRangeFilter),
            ("stats_all__total_token", CustomRangeFilter),
            ("stats_all__token_avg_buy_amount", CustomRangeFilter),
            ("stats_all__token_avg_profit_usd", CustomRangeFilter),
            ("stats_all__pnl_gt_5x_percent", CustomRangeFilter),
            ("stats_all__token_first_buy_median_price_usd", CustomRangeFilter),
            ("stats_all__token_buy_sell_duration_median", CustomRangeFilter),
            ("stats_7d__winrate", CustomRangeFilter),
            ("stats_7d__total_profit_usd", CustomRangeFilter),
            ("stats_7d__total_profit_multiplier", CustomRangeFilter),
            ("stats_7d__total_token", CustomRangeFilter),
            ("stats_7d__token_avg_buy_amount", CustomRangeFilter),
            ("stats_7d__token_avg_profit_usd", CustomRangeFilter),
            ("stats_7d__pnl_gt_5x_percent", CustomRangeFilter),
            ("stats_7d__token_first_buy_median_price_usd", CustomRangeFilter),
            ("stats_7d__token_buy_sell_duration_median", CustomRangeFilter),
            ("stats_30d__winrate", CustomRangeFilter),
            ("stats_30d__total_profit_usd", CustomRangeFilter),
            ("stats_30d__total_profit_multiplier", CustomRangeFilter),
            ("stats_30d__total_token", CustomRangeFilter),
            ("stats_30d__token_avg_buy_amount", CustomRangeFilter),
            ("stats_30d__token_avg_profit_usd", CustomRangeFilter),
            ("stats_30d__pnl_gt_5x_percent", CustomRangeFilter),
            ("stats_30d__token_first_buy_median_price_usd", CustomRangeFilter),
            ("stats_30d__token_buy_sell_duration_median", CustomRangeFilter),
            TokensIntersectionFilter,
            IsFavoriteFilter,
            IsWatchLaterFilter,
            IsBlacklistedFilter,
            IsScammerFilter,
            IsBotFilter,
            PeriodFilter,
        ]

    actions_row = ["open_stats", "open_gmgn", "open_cielo", "open_solscan"]
    actions = [
        "export_wallets_to_file",
        "add_wallets_to_favorites",
        "remove_wallets_from_favorites",
        "add_wallets_to_blacklist",
        "remove_wallets_from_blacklist",
        "add_wallets_to_watch_later",
        "remove_wallets_from_watch_later",
    ]  # Добавляем кастомное действие

    def changelist_view(self, request, extra_context=None):
        # Проверяем, применен ли фильтр
        # if not request.GET:
        #     return HttpResponseRedirect(
        #         f"{reverse('admin:solana_wallet_changelist')}?period=30d&is_scammer=0&is_bot=0&is_blacklisted=0"
        #     )

        period = request.GET.get("period", "all")

        # Дополняем контекст, если фильтр активен
        extra_context = extra_context or {}
        if period:
            extra_context["period_title_value"] = PERIODS[period]
            extra_context["selected_period"] = period
            extra_context["period_buttons"] = self.get_period_buttons(period)

        return super().changelist_view(request, extra_context=extra_context)

    def get_period_buttons(self, selected_period):
        # Список возможных периодов
        periods = ["daily", "weekly", "monthly"]
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

    def get_list_display(self, request):
        period = request.GET.get("period", "all")
        if period == "7d":
            return [
                "wallet_display",
                "stats_7d__winrate_display",
                "stats_all__winrate_display",
                "stats_7d__total_profit_usd_display",
                "stats_7d__total_profit_multiplier_display",
                "stats_7d__pnl_gt_5x_display",
                "stats_7d__pnl_2x_5x_display",
                "stats_7d__pnl_lt_2x_display",
                "stats_7d__pnl_minus_dot5_0_display",
                "stats_7d__pnl_lt_minus_dot5_display",
                "stats_7d__total_token_display",
                "stats_7d__token_avg_buy_amount_display",
                "stats_7d__token_avg_profit_usd_display",
                "stats_7d__token_first_buy_median_price_usd_display",
                "stats_7d__token_buy_sell_duration_median_display",
                "last_update_display",
            ]
        elif period == "30d":
            return [
                "wallet_display",
                "stats_30d__winrate_display",
                "stats_all__winrate_display",
                "stats_30d__total_profit_usd_display",
                "stats_30d__total_profit_multiplier_display",
                "stats_30d__pnl_gt_5x_display",
                "stats_30d__pnl_2x_5x_display",
                "stats_30d__pnl_lt_2x_display",
                "stats_30d__pnl_minus_dot5_0_display",
                "stats_30d__pnl_lt_minus_dot5_display",
                "stats_30d__total_token_display",
                "stats_30d__token_avg_buy_amount_display",
                "stats_30d__token_avg_profit_usd_display",
                "stats_30d__token_first_buy_median_price_usd_display",
                "stats_30d__token_buy_sell_duration_median_display",
                "last_update_display",
            ]
        else:
            return [
                "wallet_display",
                "stats_all__winrate_display",
                "stats_all__winrate_display",
                "stats_all__total_profit_usd_display",
                "stats_all__total_profit_multiplier_display",
                "stats_all__pnl_gt_5x_display",
                "stats_all__pnl_2x_5x_display",
                "stats_all__pnl_lt_2x_display",
                "stats_all__pnl_minus_dot5_0_display",
                "stats_all__pnl_lt_minus_dot5_display",
                "stats_all__total_token_display",
                "stats_all__token_avg_buy_amount_display",
                "stats_all__token_avg_profit_usd_display",
                "stats_all__token_first_buy_median_price_usd_display",
                "stats_all__token_buy_sell_duration_median_display",
                "last_update_display",
            ]

    def get_urls(self):
        return [
            path(
                "<str:wallet_address>/statistics/",
                WalletStatisticView.as_view(
                    model_admin=self
                ),  # IMPORTANT: model_admin is required
                name="wallet_statistic_view",
            ),
        ] + super().get_urls()


@admin.register(WalletBuyPriceGt15k)
class WalletBuyPriceGt15kAdmin(
    WalletStatsDisplays,
    WalletDisplays,
    WalletActions,
    BaseAdminModel,
):
    list_before_template = "admin/wallet/wallet_list_before.html"
    readonly_fields = (
        "created_at",
        "updated_at",
    )
    search_fields = ("address__exact",)
    ordering = ["-created_at"]

    def get_list_filter(self, request):
        return [
            ("stats_buy_price_gt_15k_all__winrate", CustomRangeFilter),
            ("stats_buy_price_gt_15k_all__total_profit_usd", CustomRangeFilter),
            ("stats_buy_price_gt_15k_all__total_profit_multiplier", CustomRangeFilter),
            ("stats_buy_price_gt_15k_all__total_token", CustomRangeFilter),
            ("stats_buy_price_gt_15k_all__token_avg_buy_amount", CustomRangeFilter),
            ("stats_buy_price_gt_15k_all__token_avg_profit_usd", CustomRangeFilter),
            ("stats_buy_price_gt_15k_all__pnl_gt_5x_percent", CustomRangeFilter),
            (
                "stats_buy_price_gt_15k_all__token_first_buy_median_price_usd",
                CustomRangeFilter,
            ),
            (
                "stats_buy_price_gt_15k_all__token_buy_sell_duration_median",
                CustomRangeFilter,
            ),
            ("stats_buy_price_gt_15k_7d__winrate", CustomRangeFilter),
            ("stats_buy_price_gt_15k_7d__total_profit_usd", CustomRangeFilter),
            ("stats_buy_price_gt_15k_7d__total_profit_multiplier", CustomRangeFilter),
            ("stats_buy_price_gt_15k_7d__total_token", CustomRangeFilter),
            ("stats_buy_price_gt_15k_7d__token_avg_buy_amount", CustomRangeFilter),
            ("stats_buy_price_gt_15k_7d__token_avg_profit_usd", CustomRangeFilter),
            ("stats_buy_price_gt_15k_7d__pnl_gt_5x_percent", CustomRangeFilter),
            (
                "stats_buy_price_gt_15k_7d__token_first_buy_median_price_usd",
                CustomRangeFilter,
            ),
            (
                "stats_buy_price_gt_15k_7d__token_buy_sell_duration_median",
                CustomRangeFilter,
            ),
            ("stats_buy_price_gt_15k_30d__winrate", CustomRangeFilter),
            ("stats_buy_price_gt_15k_30d__total_profit_usd", CustomRangeFilter),
            ("stats_buy_price_gt_15k_30d__total_profit_multiplier", CustomRangeFilter),
            ("stats_buy_price_gt_15k_30d__total_token", CustomRangeFilter),
            ("stats_buy_price_gt_15k_30d__token_avg_buy_amount", CustomRangeFilter),
            ("stats_buy_price_gt_15k_30d__token_avg_profit_usd", CustomRangeFilter),
            ("stats_buy_price_gt_15k_30d__pnl_gt_5x_percent", CustomRangeFilter),
            (
                "stats_buy_price_gt_15k_30d__token_first_buy_median_price_usd",
                CustomRangeFilter,
            ),
            (
                "stats_buy_price_gt_15k_30d__token_buy_sell_duration_median",
                CustomRangeFilter,
            ),
            TokensIntersectionFilter,
            IsFavoriteFilter,
            IsWatchLaterFilter,
            IsBlacklistedFilter,
            IsScammerFilter,
            IsBotFilter,
            PeriodFilter,
        ]

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

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(
            stats_buy_price_gt_15k_7d__isnull=False,
            stats_buy_price_gt_15k_30d__isnull=False,
            stats_buy_price_gt_15k_all__isnull=False,
        )

    def changelist_view(self, request, extra_context=None):
        # Проверяем, применен ли фильтр
        if not request.GET:
            return HttpResponseRedirect(
                f"{reverse('admin:solana_walletbuypricegt15k_changelist')}?period=30d&is_scammer=0&is_bot=0&is_blacklisted=0"
            )

        period = request.GET.get("period", "all")

        # Дополняем контекст, если фильтр активен
        extra_context = extra_context or {}
        if period:
            extra_context["period_title_value"] = PERIODS[period]
            extra_context["selected_period"] = period
            extra_context["period_buttons"] = self.get_period_buttons(period)

        return super().changelist_view(request, extra_context=extra_context)

    def get_period_buttons(self, selected_period):
        # Список возможных периодов
        periods = ["daily", "weekly", "monthly"]
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

    def get_list_display(self, request):
        period = request.GET.get("period", "all")
        if period == "7d":
            return [
                "wallet_display",
                "stats_buy_price_gt_15k_7d__winrate_display",
                "stats_buy_price_gt_15k_all__winrate_display",
                "stats_buy_price_gt_15k_7d__total_profit_usd_display",
                "stats_buy_price_gt_15k_7d__total_profit_multiplier_display",
                "stats_buy_price_gt_15k_7d__pnl_gt_5x_display",
                "stats_buy_price_gt_15k_7d__pnl_2x_5x_display",
                "stats_buy_price_gt_15k_7d__pnl_lt_2x_display",
                "stats_buy_price_gt_15k_7d__pnl_minus_dot5_0_display",
                "stats_buy_price_gt_15k_7d__pnl_lt_minus_dot5_display",
                "stats_buy_price_gt_15k_7d__total_token_display",
                "stats_buy_price_gt_15k_7d__token_avg_buy_amount_display",
                "stats_buy_price_gt_15k_7d__token_avg_profit_usd_display",
                "stats_buy_price_gt_15k_7d__token_first_buy_median_price_usd_display",
                "stats_buy_price_gt_15k_7d__token_buy_sell_duration_median_display",
                "last_update_display",
            ]
        elif period == "30d":
            return [
                "wallet_display",
                "stats_buy_price_gt_15k_30d__winrate_display",
                "stats_buy_price_gt_15k_all__winrate_display",
                "stats_buy_price_gt_15k_30d__total_profit_usd_display",
                "stats_buy_price_gt_15k_30d__total_profit_multiplier_display",
                "stats_buy_price_gt_15k_30d__pnl_gt_5x_display",
                "stats_buy_price_gt_15k_30d__pnl_2x_5x_display",
                "stats_buy_price_gt_15k_30d__pnl_lt_2x_display",
                "stats_buy_price_gt_15k_30d__pnl_minus_dot5_0_display",
                "stats_buy_price_gt_15k_30d__pnl_lt_minus_dot5_display",
                "stats_buy_price_gt_15k_30d__total_token_display",
                "stats_buy_price_gt_15k_30d__token_avg_buy_amount_display",
                "stats_buy_price_gt_15k_30d__token_avg_profit_usd_display",
                "stats_buy_price_gt_15k_30d__token_first_buy_median_price_usd_display",
                "stats_buy_price_gt_15k_30d__token_buy_sell_duration_median_display",
                "last_update_display",
            ]
        else:
            return [
                "wallet_display",
                "stats_buy_price_gt_15k_all__winrate_display",
                "stats_buy_price_gt_15k_all__winrate_display",
                "stats_buy_price_gt_15k_all__total_profit_usd_display",
                "stats_buy_price_gt_15k_all__total_profit_multiplier_display",
                "stats_buy_price_gt_15k_all__pnl_gt_5x_display",
                "stats_buy_price_gt_15k_all__pnl_2x_5x_display",
                "stats_buy_price_gt_15k_all__pnl_lt_2x_display",
                "stats_buy_price_gt_15k_all__pnl_minus_dot5_0_display",
                "stats_buy_price_gt_15k_all__pnl_lt_minus_dot5_display",
                "stats_buy_price_gt_15k_all__total_token_display",
                "stats_buy_price_gt_15k_all__token_avg_buy_amount_display",
                "stats_buy_price_gt_15k_all__token_avg_profit_usd_display",
                "stats_buy_price_gt_15k_all__token_first_buy_median_price_usd_display",
                "stats_buy_price_gt_15k_all__token_buy_sell_duration_median_display",
                "last_update_display",
            ]

    def get_urls(self):
        return [
            path(
                "<str:wallet_address>/statistics/",
                WalletStatisticBuyPriceGt15kView.as_view(
                    model_admin=self
                ),  # IMPORTANT: model_admin is required
                name="wallet_statistic_view",
            ),
        ] + super().get_urls()

    @action(
        description=_("Статистика"),
        url_path="changelist-wallet-open-stats",
        attrs={"target": "_blank"},
    )
    def open_stats(self, request: HttpRequest, object_id: int):
        obj = self.model.objects.get(pk=object_id)
        new_url = (
            reverse("admin:solana_walletbuypricegt15k_changelist")
            + f"{obj.address}/statistics/"
        )
        return redirect(new_url)
