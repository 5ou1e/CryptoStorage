from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import F
from django.http import Http404
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView
from solana.models import Wallet, WalletTokenStatistic
from unfold.contrib.filters.admin import (DropdownFilter, FieldTextFilter,
                                          RangeNumericFilter)
from unfold.views import UnfoldModelAdminViewMixin

from ..shared import change_list
from .services import get_wallet_statistics_data


class WalletStatisticView(UnfoldModelAdminViewMixin, TemplateView):
    title = "Статистика кошелька"  # required: custom page header title
    model = WalletTokenStatistic
    template_name = 'admin/wallet/statistic.html'
    permission_required = () # required: tuple of permissions

    @method_decorator(staff_member_required)  # Проверяет, что пользователь аутентифицирован и имеет is_staff=True
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        # Фильтруем записи, которые должны отображаться
        user = self.request.user
        wallet_address = self.kwargs['wallet_address']
        wallet = Wallet.objects.filter(address=wallet_address).first()
        if not wallet:
            raise Http404("Кошелёк не найден")
        tokens_queryset = WalletTokenStatistic.objects.filter(wallet=wallet)
        wallet_data = get_wallet_statistics_data(user, wallet)

        try:
            # Получаем changelist с фильтрацией и настройками отображения
            cl = change_list.get_change_list(
                title="Token activities",
                request=self.request,
                queryset=tokens_queryset,
                ordering=['-last_activity_timestamp'],
                list_display=['token_name_display',
                              'total_buy_amount_usd_display',
                              'total_sell_amount_usd_display',
                              'total_profit_usd_display',
                              'total_profit_percent_display',
                              'total_buys_count_display',
                              'total_sales_count_display',
                              'first_buy_sell_duration_display',
                              'first_buy_price_usd_display',
                              'first_sell_price_usd_display',
                              'first_buy_timestamp_display',
                              'first_sell_timestamp_display',
                              # 'last_activity_timestamp_display',
                              'actions_display',
                              ],
                list_display_links=None,
                search_fields=["token__name", "token__address", "wallet__address"],
                list_filter=[
                    ("token__name", FieldTextFilter),
                    ("token__address", FieldTextFilter),
                    ("total_profit_usd", RangeNumericFilter),
                    ("total_profit_percent", RangeNumericFilter),
                    ('total_buys_count', RangeNumericFilter),
                    ('total_sales_count', RangeNumericFilter),
                    ("first_buy_sell_duration", RangeNumericFilter),
                    ('first_buy_price_usd', RangeNumericFilter),
                    ('first_sell_price_usd', RangeNumericFilter),
                    ('total_swaps_from_txs_with_mt_3_swappers', RangeNumericFilter),
                    ('total_swaps_from_arbitrage_swap_events', RangeNumericFilter),
                    IsTokenSellAmountGtBuyAmountFilter
                ],
                list_filter_sheet=True,
                list_filter_submit=True,
                date_hierarchy=None,
            )
        except change_list.IncorrectLookupParameters:
            # В случае ошибки перенаправляем на главную страницу
            return redirect("/")

        # Получаем базовый контекст от родительского класса
        context = super().get_context_data(**kwargs)

        # Добавляем все необходимые данные в контекст
        context.update({"cl": cl,
                        "opts": cl.opts,
                        "actions_on_top": True,
                        "wallet": wallet_data,
                        })

        return context


class WalletStatisticBuyPriceGt15kView(WalletStatisticView):

    def get_context_data(self, **kwargs):
        # Фильтруем записи, которые должны отображаться
        user = self.request.user
        wallet_address = self.kwargs['wallet_address']
        wallet = Wallet.objects.filter(address=wallet_address).first()
        if not wallet:
            raise Http404("Кошелёк не найден")
        tokens_queryset = WalletTokenStatistic.objects.filter(
            wallet=wallet,
            first_buy_price_usd__gte=0.000008,
            total_buy_amount_usd__gte=100,
        )
        wallet_data = get_wallet_statistics_data(user, wallet, use_buy_price_gt_20k_stats=True)

        try:
            # Получаем changelist с фильтрацией и настройками отображения
            cl = change_list.get_change_list(
                title="Token activities",
                request=self.request,
                queryset=tokens_queryset,
                ordering=['-last_activity_timestamp'],
                list_display=['token_name_display',
                              'total_buy_amount_usd_display',
                              'total_sell_amount_usd_display',
                              'total_profit_usd_display',
                              'total_profit_percent_display',
                              'total_buys_count_display',
                              'total_sales_count_display',
                              'first_buy_sell_duration_display',
                              'first_buy_price_usd_display',
                              'first_sell_price_usd_display',
                              'first_buy_timestamp_display',
                              'first_sell_timestamp_display',
                              # 'last_activity_timestamp_display',
                              'actions_display',
                              ],
                list_display_links=None,
                search_fields=["token__name", "token__address", "wallet__address"],
                list_filter=[
                    ("token__name", FieldTextFilter),
                    ("token__address", FieldTextFilter),
                    ("total_profit_usd", RangeNumericFilter),
                    ("total_profit_percent", RangeNumericFilter),
                    ('total_buys_count', RangeNumericFilter),
                    ('total_sales_count', RangeNumericFilter),
                    ("first_buy_sell_duration", RangeNumericFilter),
                    ('first_buy_price_usd', RangeNumericFilter),
                    ('first_sell_price_usd', RangeNumericFilter),
                    ('total_swaps_from_txs_with_mt_3_swappers', RangeNumericFilter),
                    ('total_swaps_from_arbitrage_swap_events', RangeNumericFilter),
                    IsTokenSellAmountGtBuyAmountFilter
                ],
                list_filter_sheet=True,
                list_filter_submit=True,
                date_hierarchy=None,
            )
        except change_list.IncorrectLookupParameters:
            # В случае ошибки перенаправляем на главную страницу
            return redirect("/")

        # Получаем базовый контекст от родительского класса
        context = super().get_context_data(**kwargs)

        # Добавляем все необходимые данные в контекст
        context.update({"cl": cl,
                        "opts": cl.opts,
                        "actions_on_top": True,
                        "wallet": wallet_data,
                        })

        return context

class IsTokenSellAmountGtBuyAmountFilter(DropdownFilter):
    title = _("Сумма продаж > суммы покупок (в единицах токена)")
    parameter_name = "is_token_sell_amount_gt_buy_amount"

    def lookups(self, request, model_admin):
        return [
            ["0", _("Нет")],
            ["1", _("Да")],
        ]

    def queryset(self, request, queryset):
        if self.value() == '1':
            return queryset.filter(
                total_sell_amount_token__gt=F('total_buy_amount_token')*1.01,
                total_buys_count__gt=0
            )
        if self.value() == '0':
            return queryset.exclude(
                total_sell_amount_token__gt=F('total_buy_amount_token')*1.01,
                total_buys_count__gt=0
            )

        return queryset
