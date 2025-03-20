
from django.contrib import admin
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.urls import path, reverse
from django.utils.html import mark_safe
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin
from unfold.contrib.filters.admin import FieldTextFilter, RangeDateTimeFilter
from unfold.decorators import action, display
from users.models import UserWallet
from utils.number_utils import formatted_number, round_to_first_non_zero
from utils.time_utils import formatted_duration

from ...models import Wallet, WalletBuyPriceGt15k, WalletProxy
from ..shared.misc import LargeTablePaginator
from .filters import (CustomRangeFilter, IsBlacklistedFilter, IsBotFilter,
                      IsFavoriteFilter, IsScammerFilter, IsWatchLaterFilter,
                      PeriodFilter, TokensIntersectionFilter)
from .inlines import (WalletPeriodStatistic7dInline,
                      WalletPeriodStatistic30dInline,
                      WalletPeriodStatisticAllInline,
                      WalletTokenStatisticInline)
from .views import WalletStatisticBuyPriceGt15kView, WalletStatisticView

PERIODS = {
    '7d': '7 дней',
    '30d': '30 дней',
    'all': 'Все время'
}

DISPLAY_LABELS = {
    'good': "success",
    'warning': "warning",
    'bad': "danger",
    'ok': "default",
}


@admin.register(WalletProxy)
class WalletProxyAdmin(ModelAdmin):
    inlines = [
        WalletPeriodStatistic7dInline,
        WalletPeriodStatistic30dInline,
        WalletPeriodStatisticAllInline,
        WalletTokenStatisticInline,
    ]
    show_full_result_count = False
    paginator = LargeTablePaginator
    readonly_fields = ('last_stats_check','created_at', 'updated_at', )
    list_display = ('address', 'last_stats_check')
    list_display_links = ('address',)
    search_fields = ('address__exact',)
    list_filter_submit = True  # Submit button at the bottom of the filter
    from django.contrib.admin import DateFieldListFilter
    list_filter = [
        ("address", FieldTextFilter),
        ("last_stats_check", DateFieldListFilter),
        ('created_at', RangeDateTimeFilter),
    ]


@admin.register(Wallet)
class WalletAdmin(ModelAdmin):
    change_list_template = 'admin/wallet/change_list.html'
    inlines = []
    list_per_page = 20
    show_full_result_count = False
    paginator = LargeTablePaginator
    readonly_fields = ('created_at', 'updated_at',)
    search_fields = ('address__exact',)
    list_filter_submit = True
    list_filter_sheet = True
    list_fullwidth = True
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
    actions = ['export_field_to_buffer',
               'add_wallets_to_self_favorites',
               'remove_wallets_from_self_favorites',
               'add_wallets_to_self_blacklist',
               'remove_wallets_from_self_blacklist',
               ]  # Добавляем кастомное действие



    def changelist_view(self, request, extra_context=None):
        # Проверяем, применен ли фильтр
        if not request.GET:
            return HttpResponseRedirect(f"{reverse('admin:solana_wallet_changelist')}?period=30d&is_scammer=0&is_bot=0&is_blacklisted=0")

        period = request.GET.get('period', 'all')

        # Дополняем контекст, если фильтр активен
        extra_context = extra_context or {}
        if period:
            extra_context['period_title_value'] = PERIODS[period]
            extra_context['selected_period'] = period
            extra_context['period_buttons'] = self.get_period_buttons(period)

        return super().changelist_view(request, extra_context=extra_context)

    def get_period_buttons(self, selected_period):
        # Список возможных периодов
        periods = ['daily', 'weekly', 'monthly']
        buttons = []

        # Формируем список кнопок
        for period in PERIODS:
            active_class = 'active' if period == selected_period else ''
            button = {
                'period': period,
                'active_class': active_class,
                'label': PERIODS[period].capitalize()
            }
            buttons.append(button)

        return buttons

    def get_list_display(self, request):
        self.period = request.GET.get('period', 'all')
        if self.period == '7d':
            return ['wallet_display',
                    'winrate_7d_display',
                    'winrate_all_display',
                    'total_profit_usd_7d_display',
                    'total_profit_multiplier_7d_display',
                    'pnl_gt_5x_num_7d_display',
                    'pnl_2x_5x_num_7d_display',
                    'pnl_lt_2x_num_7d_display',
                    'pnl_minus_dot5_0x_num_7d_display',
                    'pnl_lt_minus_dot5_num_7d_display',
                    'total_token_7d_display',
                    # 'sol_balance_display',
                    'token_avg_buy_amount_7d_display',
                    'token_avg_profit_usd_7d_display',
                    'token_first_buy_median_price_usd_7d_display',
                    'token_buy_sell_duration_median_7d_display',
                    'last_update_display',
                    ]
        elif self.period == '30d':
            return ['wallet_display',
                    'winrate_30d_display',
                    'winrate_all_display',
                    'total_profit_usd_30d_display',
                    'total_profit_multiplier_30d_display',
                    'pnl_gt_5x_num_30d_display',
                    'pnl_2x_5x_num_30d_display',
                    'pnl_lt_2x_num_30d_display',
                    'pnl_minus_dot5_0x_num_30d_display',
                    'pnl_lt_minus_dot5_num_30d_display',
                    'total_token_30d_display',
                    # 'sol_balance_display',
                    'token_avg_buy_amount_30d_display',
                    'token_avg_profit_usd_30d_display',
                    'token_first_buy_median_price_usd_30d_display',
                    'token_buy_sell_duration_median_30d_display',
                    'last_update_display',
                    ]
        else:
            return ['wallet_display',
                    'winrate_all_display',
                    'winrate_all_display',
                    'total_profit_usd_all_display',
                    'total_profit_multiplier_all_display',
                    'pnl_gt_5x_num_all_display',
                    'pnl_2x_5x_num_all_display',
                    'pnl_lt_2x_num_all_display',
                    'pnl_minus_dot5_0x_num_all_display',
                    'pnl_lt_minus_dot5_num_all_display',
                    'total_token_all_display',
                    # 'sol_balance_display',
                    'token_avg_buy_amount_all_display',
                    'token_avg_profit_usd_all_display',
                    'token_first_buy_median_price_usd_all_display',
                    'token_buy_sell_duration_median_all_display',
                    'last_update_display',
                    ]

    def get_urls(self):
        return [
            path(
                '<str:wallet_address>/statistics/',
                WalletStatisticView.as_view(model_admin=self),  # IMPORTANT: model_admin is required
                name="wallet_statistic_view"
            ),
        ] + super().get_urls()

    @action(description="Выгрузить адреса кошельков")
    def export_field_to_buffer(self, request, queryset):
        # Собираем данные из всех выбранных записей
        data = "\n".join(str(obj.address) for obj in queryset)

        # Возвращаем данные в виде текстового файла
        response = HttpResponse(data, content_type="text/plain")
        response['Content-Disposition'] = 'attachment; filename="exported_data.txt"'
        return response

    @action(description="Добавить в блек-лист")
    def add_wallets_to_self_blacklist(self, request, queryset):
        for obj in queryset:
            user_wallet, created = UserWallet.objects.get_or_create(user=request.user, wallet_id=obj.id)
            user_wallet.is_blacklisted = True
            user_wallet.save()

    @action(description="Убрать из блек-листа")
    def remove_wallets_from_self_blacklist(self, request, queryset):
        for obj in queryset:
            user_wallet, created = UserWallet.objects.get_or_create(user=request.user, wallet_id=obj.id)
            user_wallet.is_blacklisted = False
            user_wallet.save()

    @action(description="Добавить в избранное")
    def add_wallets_to_self_favorites(self, request, queryset):
        for obj in queryset:
            user_wallet, created = UserWallet.objects.get_or_create(user=request.user, wallet_id=obj.id)
            user_wallet.is_favorite = True
            user_wallet.save()

    @action(description="Убрать из избранных")
    def remove_wallets_from_self_favorites(self, request, queryset):
        for obj in queryset:
            user_wallet, created = UserWallet.objects.get_or_create(user=request.user, wallet_id=obj.id)
            user_wallet.is_favorite = False
            user_wallet.save()

    @action(
        description=_("Статистика"),
        url_path="changelist-wallet-open-stats",
        attrs={"target": "_blank"}
    )
    def open_stats(self, request: HttpRequest, object_id: int):
        obj = self.model.objects.get(pk=object_id)
        # Формируем корректный URL с помощью reverse
        new_url = reverse(
            'admin:solana_wallet_changelist'
        ) + f"{obj.address}/statistics/"
        return redirect(new_url)

    @action(
        description=_("Открыть на GMGN"),
        url_path="changelist-wallet-open-gmgn",
        attrs={"target": "_blank"}
    )
    def open_gmgn(self, request: HttpRequest, object_id: int):
        obj = self.model.objects.get(pk=object_id)
        wallet_address = obj.address  # Если поле называется `address`
        return redirect(
            f"https://gmgn.ai/sol/address/{wallet_address}"
        )

    @action(
        description=_("Открыть на Cielo"),
        url_path="changelist-wallet-open-cielo",
        attrs={"target": "_blank"}
    )
    def open_cielo(self, request: HttpRequest, object_id: int):
        obj = self.model.objects.get(pk=object_id)
        wallet_address = obj.address  # Если поле называется `address`
        return redirect(
            f"https://app.cielo.finance/profile/{wallet_address}"
        )

    @action(
        description=_("Открыть на Solscan"),
        url_path="changelist-wallet-open-solscan",
        attrs={"target": "_blank"}
    )
    def open_solscan(self, request: HttpRequest, object_id: int):
        obj = self.model.objects.get(pk=object_id)
        wallet_address = obj.address  # Если поле называется `address`
        return redirect(
            f"https://solscan.io/account/{wallet_address}"
        )

    @display(
        description=_("Кошелек"),
        ordering="-address",
    )
    def wallet_display(self, obj):
        copy_button = render_to_string(
            'admin/copy_button.html',
            {
                'copy_value':obj.address,
            }  # передаем нужные данные в контекст
        )
        value = f'''
                    <div class="flex gap-1 font-semibold text-font-default-light dark:text-font-default-dark">
                        <a href="{obj.get_absolute_url()} " title="{obj.address}" target="_blank">{obj.address[:5]}...{obj.address[-2:]}</a>
                        <span class="text-font-subtle-light dark:text-font-subtle-dark">{copy_button}</span>
                    </div>
                '''
        return mark_safe(value)

    @display(
        description=_("Обн"),
        ordering="-last_stats_check",
    )
    def last_update_display(self, obj):
        last_stats_update_title = obj.last_stats_check
        last_stats_update_value = formatted_duration(now() - obj.last_stats_check) + " назад" if obj.last_stats_check else '-'
        value = f'''
                <div>
                    <p class="text-base " title="{ last_stats_update_title }" class="text-base text-sm text-font-subtle-light dark:text-font-subtle-dark">{ last_stats_update_value }</p>
                </div>
                '''
        return mark_safe(value)


    @display(
        description=_("Баланс"),
        ordering="-sol_balance",
    )
    def sol_balance_display(self, obj):
        value = round_to_first_non_zero(obj.details.sol_balance)
        return f'{value} SOL' if value else '0.00 SOL'

    @display(
        description=_("В/р Все"),
        ordering="-stats_all__winrate",
        label={
            'good': "success",
            'bad': "danger",
        },
    )
    def winrate_all_display(self, obj):
        if obj.stats_all.winrate is None:
            return None
        value = round(obj.stats_all.winrate, 2)
        return 'good' if value >= 50 else 'bad', f'{value} %'

    @display(
        description=_("Профит $"),
        ordering="-stats_all__total_profit_usd",
    )
    def total_profit_usd_all_display(self, obj):
        value = obj.stats_all.total_profit_usd
        if not value:
            return None
        return formatted_number(value, suffix=' $', add_sign=True)

    @display(
        description=_("Профит %"),
        ordering="-stats_all__total_profit_multiplier",
        label=DISPLAY_LABELS,
    )
    def total_profit_multiplier_all_display(self, obj):
        value = obj.stats_all.total_profit_multiplier
        if not value:
            return None
        return 'good' if value >= 1 else 'ok' if value >= 0 else 'bad', formatted_number(value, suffix=' %', add_sign=True)

    @display(
        description=_("Токенов"),
        ordering="-stats_all__total_token",
    )
    def total_token_all_display(self, obj):
        return obj.stats_all.total_token

    @display(
        description=_("<-50"),
        ordering="-stats_all__pnl_lt_minus_dot5_percent",
    label=DISPLAY_LABELS,
    )
    def pnl_lt_minus_dot5_num_all_display(self, obj):
        value = obj.stats_all.pnl_lt_minus_dot5_percent
        return 'bad', formatted_number(value, decimals=1, zero_value='-', suffix=" %")

    @display(
        description=_("0 - -50"),
        ordering="-stats_all__pnl_minus_dot5_0x_percent",
        label=DISPLAY_LABELS,
    )
    def pnl_minus_dot5_0x_num_all_display(self, obj):
        value = obj.stats_all.pnl_minus_dot5_0x_percent
        return 'bad', formatted_number(value, decimals=1, zero_value='-', suffix=" %")

    @display(
        description=_("0 - 200"),
        ordering="-stats_all__pnl_lt_2x_percent",
        label=DISPLAY_LABELS,
    )
    def pnl_lt_2x_num_all_display(self, obj):
        value = obj.stats_all.pnl_lt_2x_percent
        return 'good', formatted_number(value, decimals=1, zero_value='-', suffix=" %")

    @display(
        description=_("200 - 500"),
        ordering="-stats_all__pnl_2x_5x_percent",
        label=DISPLAY_LABELS,
    )
    def pnl_2x_5x_num_all_display(self, obj):
        value = obj.stats_all.pnl_2x_5x_percent
        return 'good', formatted_number(value, decimals=1, zero_value='-', suffix=" %")

    @display(
        description=_(">500"),
        ordering="-stats_all__pnl_gt_5x_percent",
        label=DISPLAY_LABELS,
    )
    def pnl_gt_5x_num_all_display(self, obj):
        value = obj.stats_all.pnl_gt_5x_percent
        return 'good', formatted_number(value, decimals=1, zero_value='-', suffix=" %")

    @display(
        description=_("Ср. пок."),
        ordering="-stats_all__token_avg_buy_amount",
    )
    def token_avg_buy_amount_all_display(self, obj):
        value = obj.stats_all.token_avg_buy_amount
        median = obj.stats_all.token_median_buy_amount
        if not value:
            return None
        return formatted_number(value, suffix=' $')  # + f" ({formatted_number(median, suffix=' $')})"

    @display(
        description=_("Холд мед."),
        ordering="-stats_all__token_buy_sell_duration_median",
        label=DISPLAY_LABELS,
    )
    def token_buy_sell_duration_median_all_display(self, obj):
        value = obj.stats_all.token_buy_sell_duration_median
        return ('ok' if value > 30 else 'warning' if value > 5 else 'bad', formatted_duration(value)) if value is not None else None

    @display(
        description=_("Ср. профит"),
        ordering="-stats_all__token_avg_profit_usd",
    )
    def token_avg_profit_usd_all_display(self, obj):
        value = obj.stats_all.token_avg_profit_usd
        if not value:
            return None
        return formatted_number(value, suffix=' $', add_sign=True)

    @display(
        description=_("Сред ц.1п"),
        ordering="-stats_all__token_first_buy_median_price_usd",
    )
    def token_first_buy_median_price_usd_all_display(self, obj):
        value = obj.stats_all.token_first_buy_median_price_usd
        return formatted_number(value, decimals=10, suffix=" $", subscript=True)

    @display(
        description=_("Винрейт"),
        ordering="-stats_30d__winrate",
        label=DISPLAY_LABELS,
    )
    def winrate_30d_display(self, obj):
        if obj.stats_30d.winrate is None:
            return None
        value = round(obj.stats_30d.winrate, 2)
        return 'good' if value >= 50 else 'bad', f'{value} %'

    @display(
        description=_("Профит $"),
        ordering="-stats_30d__total_profit_usd",
    )
    def total_profit_usd_30d_display(self, obj):
        value = obj.stats_30d.total_profit_usd
        if not value:
            return None
        return formatted_number(value, suffix=' $')

    @display(
        description=_("Профит %"),
        ordering="-stats_30d__total_profit_multiplier",
        label=DISPLAY_LABELS,
    )
    def total_profit_multiplier_30d_display(self, obj):
        value = obj.stats_30d.total_profit_multiplier
        if not value:
            return None
        return 'good' if value >= 1 else 'ok' if value >= 0 else 'bad', formatted_number(value, suffix=' %')

    @display(
        description=_("Токенов"),
        ordering="-stats_30d__total_token",
    )
    def total_token_30d_display(self, obj):
        return obj.stats_30d.total_token

    @display(
        description=_("<-50"),
        ordering="-stats_30d__pnl_lt_minus_dot5_percent",
        label=DISPLAY_LABELS,
    )
    def pnl_lt_minus_dot5_num_30d_display(self, obj):
        value = obj.stats_30d.pnl_lt_minus_dot5_percent
        return 'bad', formatted_number(value, decimals=1, zero_value='-', suffix=" %")

    @display(
        description=_("0 - -50"),
        ordering="-stats_30d__pnl_minus_dot5_0x_percent",
        label=DISPLAY_LABELS,
    )
    def pnl_minus_dot5_0x_num_30d_display(self, obj):
        value = obj.stats_30d.pnl_minus_dot5_0x_percent
        return 'bad', formatted_number(value, decimals=1, zero_value='-', suffix=" %")

    @display(
        description=_("0 - 200"),
        ordering="-stats_30d__pnl_lt_2x_percent",
        label=DISPLAY_LABELS,
    )
    def pnl_lt_2x_num_30d_display(self, obj):
        value = obj.stats_30d.pnl_lt_2x_percent
        return 'good', formatted_number(value, decimals=1, zero_value='-', suffix=" %")

    @display(
        description=_("200 - 500"),
        ordering="-stats_30d__pnl_2x_5x_percent",
        label=DISPLAY_LABELS,
    )
    def pnl_2x_5x_num_30d_display(self, obj):
        value = obj.stats_30d.pnl_2x_5x_percent
        return 'good', formatted_number(value, decimals=1, zero_value='-', suffix=" %")

    @display(
        description=_(">500"),
        ordering="-stats_30d__pnl_gt_5x_percent",
        label=DISPLAY_LABELS,
    )
    def pnl_gt_5x_num_30d_display(self, obj):
        value = obj.stats_30d.pnl_gt_5x_percent
        return 'good', formatted_number(value, decimals=1, zero_value='-', suffix=" %")

    @display(
        description=_("Ср. покупка"),
        ordering="-stats_30d__token_avg_buy_amount",
    )
    def token_avg_buy_amount_30d_display(self, obj):
        value = obj.stats_30d.token_avg_buy_amount
        median = obj.stats_30d.token_median_buy_amount
        if not value:
            return None
        return formatted_number(value, suffix=' $')  # + f" ({formatted_number(median, suffix=' $')})"

    @display(
        description=_("Холд мед."),
        ordering="-stats_30d__token_buy_sell_duration_median",
        label=DISPLAY_LABELS,
    )
    def token_buy_sell_duration_median_30d_display(self, obj):
        value = obj.stats_30d.token_buy_sell_duration_median
        return ('ok' if value > 30 else 'warning' if value > 5 else 'bad', formatted_duration(value)) if value else None

    @display(
        description=_("Ср. профит"),
        ordering="-stats_30d__token_avg_profit_usd",
    )
    def token_avg_profit_usd_30d_display(self, obj):
        value = obj.stats_30d.token_avg_profit_usd
        if not value:
            return None
        return formatted_number(value, suffix=' $')

    @display(
        description=_("Сред ц.1п"),
        ordering="-stats_30d__token_first_buy_median_price_usd",
    )
    def token_first_buy_median_price_usd_30d_display(self, obj):
        value = obj.stats_30d.token_first_buy_median_price_usd
        return formatted_number(value, decimals=10, suffix=" $", subscript=True)

    @display(
        description=_("Винрейт"),
        ordering="-stats_7d__winrate",
        label=DISPLAY_LABELS,
    )
    def winrate_7d_display(self, obj):
        if obj.stats_7d.winrate is None:
            return None
        value = round(obj.stats_7d.winrate, 2)
        return 'good' if value >= 50 else 'bad', f'{value} %'

    @display(
        description=_("Профит $"),
        ordering="-stats_7d__total_profit_usd",
    )
    def total_profit_usd_7d_display(self, obj):
        value = obj.stats_7d.total_profit_usd
        if not value:
            return None
        return formatted_number(value, suffix=' $')

    @display(
        description=_("Профит %"),
        ordering="-stats_7d__total_profit_multiplier",
        label=DISPLAY_LABELS,
    )
    def total_profit_multiplier_7d_display(self, obj):
        value = obj.stats_7d.total_profit_multiplier
        if not value:
            return None
        return 'good' if value >= 1 else 'ok' if value >= 0 else 'bad', formatted_number(value, suffix=' %')

    @display(
        description=_("Токенов"),
        ordering="-stats_7d__total_token",
    )
    def total_token_7d_display(self, obj):
        return obj.stats_7d.total_token

    @display(
        description=_("<-50"),
        ordering="-stats_7d__pnl_lt_minus_dot5_percent",
        label=DISPLAY_LABELS,
    )
    def pnl_lt_minus_dot5_num_7d_display(self, obj):
        value = obj.stats_7d.pnl_lt_minus_dot5_percent
        return 'bad', formatted_number(value, decimals=1, zero_value='-', suffix=" %")

    @display(
        description=_("0 - -50"),
        ordering="-stats_7d__pnl_minus_dot5_0x_percent",
        label=DISPLAY_LABELS,
    )
    def pnl_minus_dot5_0x_num_7d_display(self, obj):
        value = obj.stats_7d.pnl_minus_dot5_0x_percent
        return 'bad', formatted_number(value, decimals=1, zero_value='-', suffix=" %")

    @display(
        description=_("0 - 200"),
        ordering="-stats_7d__pnl_lt_2x_percent",
        label=DISPLAY_LABELS,
    )
    def pnl_lt_2x_num_7d_display(self, obj):
        value = obj.stats_7d.pnl_lt_2x_percent
        return 'good', formatted_number(value, decimals=1, zero_value='-', suffix=" %")

    @display(
        description=_("200 - 500"),
        ordering="-stats_7d__pnl_2x_5x_percent",
        label=DISPLAY_LABELS,
    )
    def pnl_2x_5x_num_7d_display(self, obj):
        value = obj.stats_7d.pnl_2x_5x_percent
        return 'good', formatted_number(value, decimals=1, zero_value='-', suffix=" %")

    @display(
        description=_(">500"),
        ordering="-stats_7d__pnl_gt_5x_percent",
        label=DISPLAY_LABELS,
    )
    def pnl_gt_5x_num_7d_display(self, obj):
        value = obj.stats_7d.pnl_gt_5x_percent
        return 'good', formatted_number(value, decimals=1, zero_value='-', suffix=" %")

    @display(
        description=_("Ср. покупка"),
        ordering="-stats_7d__token_avg_buy_amount",
    )
    def token_avg_buy_amount_7d_display(self, obj):
        value = obj.stats_7d.token_avg_buy_amount
        median = obj.stats_7d.token_median_buy_amount
        if not value:
            return None
        return formatted_number(value, suffix=' $')  # + f" ({formatted_number(median, suffix=' $')})"

    @display(
        description=_("Холд мед."),
        ordering="-stats_7d__token_buy_sell_duration_median",
        label=DISPLAY_LABELS,
    )
    def token_buy_sell_duration_median_7d_display(self, obj):
        value = obj.stats_7d.token_buy_sell_duration_median
        return ('ok' if value > 30 else 'warning' if value > 5 else 'bad', formatted_duration(value)) if value else None  # + f" ({formatted_duration(median)})"

    @display(
        description=_("Ср. профит"),
        ordering="-stats_7d__token_avg_profit_usd",
    )
    def token_avg_profit_usd_7d_display(self, obj):
        value = obj.stats_7d.token_avg_profit_usd
        if not value:
            return None
        return formatted_number(value, suffix=' $')

    @display(
        description=_("Сред ц.1п"),
        ordering="-stats_7d__token_first_buy_median_price_usd",
    )
    def token_first_buy_median_price_usd_7d_display(self, obj):
        value = obj.stats_7d.token_first_buy_median_price_usd
        return formatted_number(value, decimals=10, suffix=" $", subscript=True)


@admin.register(WalletBuyPriceGt15k)
class WalletBuyPriceGt15kAdmin(ModelAdmin):
    change_list_template = 'admin/wallet/change_list.html'
    inlines = []
    list_per_page = 20
    show_full_result_count = False
    paginator = LargeTablePaginator
    readonly_fields = ('created_at', 'updated_at',)
    search_fields = ('address__exact',)
    list_filter_submit = True
    list_filter_sheet = True
    list_fullwidth = True
    ordering = ["-created_at"]

    def get_list_filter(self, request):
        return [
            # ("details__sol_balance", CustomRangeFilter),
            ("stats_buy_price_gt_15k_all__winrate", CustomRangeFilter),
            ("stats_buy_price_gt_15k_all__total_profit_usd", CustomRangeFilter),
            ("stats_buy_price_gt_15k_all__total_profit_multiplier", CustomRangeFilter),
            ("stats_buy_price_gt_15k_all__total_token", CustomRangeFilter),
            ("stats_buy_price_gt_15k_all__token_avg_buy_amount", CustomRangeFilter),
            ("stats_buy_price_gt_15k_all__token_avg_profit_usd", CustomRangeFilter),
            ("stats_buy_price_gt_15k_all__pnl_gt_5x_percent", CustomRangeFilter),
            ("stats_buy_price_gt_15k_all__token_first_buy_median_price_usd", CustomRangeFilter),
            ("stats_buy_price_gt_15k_all__token_buy_sell_duration_median", CustomRangeFilter),

            ("stats_buy_price_gt_15k_7d__winrate", CustomRangeFilter),
            ("stats_buy_price_gt_15k_7d__total_profit_usd", CustomRangeFilter),
            ("stats_buy_price_gt_15k_7d__total_profit_multiplier", CustomRangeFilter),
            ("stats_buy_price_gt_15k_7d__total_token", CustomRangeFilter),
            ("stats_buy_price_gt_15k_7d__token_avg_buy_amount", CustomRangeFilter),
            ("stats_buy_price_gt_15k_7d__token_avg_profit_usd", CustomRangeFilter),
            ("stats_buy_price_gt_15k_7d__pnl_gt_5x_percent", CustomRangeFilter),
            ("stats_buy_price_gt_15k_7d__token_first_buy_median_price_usd", CustomRangeFilter),
            ("stats_buy_price_gt_15k_7d__token_buy_sell_duration_median", CustomRangeFilter),

            ("stats_buy_price_gt_15k_30d__winrate", CustomRangeFilter),
            ("stats_buy_price_gt_15k_30d__total_profit_usd", CustomRangeFilter),
            ("stats_buy_price_gt_15k_30d__total_profit_multiplier", CustomRangeFilter),
            ("stats_buy_price_gt_15k_30d__total_token", CustomRangeFilter),
            ("stats_buy_price_gt_15k_30d__token_avg_buy_amount", CustomRangeFilter),
            ("stats_buy_price_gt_15k_30d__token_avg_profit_usd", CustomRangeFilter),
            ("stats_buy_price_gt_15k_30d__pnl_gt_5x_percent", CustomRangeFilter),
            ("stats_buy_price_gt_15k_30d__token_first_buy_median_price_usd", CustomRangeFilter),
            ("stats_buy_price_gt_15k_30d__token_buy_sell_duration_median", CustomRangeFilter),
            TokensIntersectionFilter,
            IsFavoriteFilter,
            IsWatchLaterFilter,
            IsBlacklistedFilter,
            IsScammerFilter,
            IsBotFilter,
            PeriodFilter,
        ]

    actions_row = ["open_stats", "open_gmgn", "open_cielo", "open_solscan"]
    actions = ['export_field_to_buffer',
               'add_wallets_to_self_favorites',
               'remove_wallets_from_self_favorites',
               'add_wallets_to_self_blacklist',
               'remove_wallets_from_self_blacklist',
               ]  # Добавляем кастомное действие

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
            return HttpResponseRedirect(f"{reverse('admin:solana_walletbuypricegt15k_changelist')}?period=30d&is_scammer=0&is_bot=0&is_blacklisted=0")

        period = request.GET.get('period', 'all')

        # Дополняем контекст, если фильтр активен
        extra_context = extra_context or {}
        if period:
            extra_context['period_title_value'] = PERIODS[period]
            extra_context['selected_period'] = period
            extra_context['period_buttons'] = self.get_period_buttons(period)

        return super().changelist_view(request, extra_context=extra_context)

    def get_period_buttons(self, selected_period):
        # Список возможных периодов
        periods = ['daily', 'weekly', 'monthly']
        buttons = []

        # Формируем список кнопок
        for period in PERIODS:
            active_class = 'active' if period == selected_period else ''
            button = {
                'period': period,
                'active_class': active_class,
                'label': PERIODS[period].capitalize()
            }
            buttons.append(button)

        return buttons

    def get_list_display(self, request):
        self.period = request.GET.get('period', 'all')
        if self.period == '7d':
            return ['wallet_display',
                    'winrate_7d_display',
                    'winrate_all_display',
                    'total_profit_usd_7d_display',
                    'total_profit_multiplier_7d_display',
                    'pnl_gt_5x_num_7d_display',
                    'pnl_2x_5x_num_7d_display',
                    'pnl_lt_2x_num_7d_display',
                    'pnl_minus_dot5_0x_num_7d_display',
                    'pnl_lt_minus_dot5_num_7d_display',
                    'total_token_7d_display',
                    # 'sol_balance_display',
                    'token_avg_buy_amount_7d_display',
                    'token_avg_profit_usd_7d_display',
                    'token_first_buy_median_price_usd_7d_display',
                    'token_buy_sell_duration_median_7d_display',
                    'last_update_display',
                    ]
        elif self.period == '30d':
            return ['wallet_display',
                    'winrate_30d_display',
                    'winrate_all_display',
                    'total_profit_usd_30d_display',
                    'total_profit_multiplier_30d_display',
                    'pnl_gt_5x_num_30d_display',
                    'pnl_2x_5x_num_30d_display',
                    'pnl_lt_2x_num_30d_display',
                    'pnl_minus_dot5_0x_num_30d_display',
                    'pnl_lt_minus_dot5_num_30d_display',
                    'total_token_30d_display',
                    # 'sol_balance_display',
                    'token_avg_buy_amount_30d_display',
                    'token_avg_profit_usd_30d_display',
                    'token_first_buy_median_price_usd_30d_display',
                    'token_buy_sell_duration_median_30d_display',
                    'last_update_display',
                    ]
        else:
            return ['wallet_display',
                    'winrate_all_display',
                    'winrate_all_display',
                    'total_profit_usd_all_display',
                    'total_profit_multiplier_all_display',
                    'pnl_gt_5x_num_all_display',
                    'pnl_2x_5x_num_all_display',
                    'pnl_lt_2x_num_all_display',
                    'pnl_minus_dot5_0x_num_all_display',
                    'pnl_lt_minus_dot5_num_all_display',
                    'total_token_all_display',
                    # 'sol_balance_display',
                    'token_avg_buy_amount_all_display',
                    'token_avg_profit_usd_all_display',
                    'token_first_buy_median_price_usd_all_display',
                    'token_buy_sell_duration_median_all_display',
                    'last_update_display',
                    ]

    def get_urls(self):
        return [
            path(
                '<str:wallet_address>/statistics/',
                WalletStatisticBuyPriceGt15kView.as_view(model_admin=self),  # IMPORTANT: model_admin is required
                name="wallet_statistic_view"
            ),
        ] + super().get_urls()

    @action(description="Выгрузить адреса кошельков")
    def export_field_to_buffer(self, request, queryset):
        # Собираем данные из всех выбранных записей
        data = "\n".join(str(obj.address) for obj in queryset)

        # Возвращаем данные в виде текстового файла
        response = HttpResponse(data, content_type="text/plain")
        response['Content-Disposition'] = 'attachment; filename="exported_data.txt"'
        return response

    @action(description="Добавить в блек-лист")
    def add_wallets_to_self_blacklist(self, request, queryset):
        for obj in queryset:
            user_wallet, created = UserWallet.objects.get_or_create(user=request.user, wallet_id=obj.id)
            user_wallet.is_blacklisted = True
            user_wallet.save()

    @action(description="Убрать из блек-листа")
    def remove_wallets_from_self_blacklist(self, request, queryset):
        for obj in queryset:
            user_wallet, created = UserWallet.objects.get_or_create(user=request.user, wallet_id=obj.id)
            user_wallet.is_blacklisted = False
            user_wallet.save()

    @action(description="Добавить в избранное")
    def add_wallets_to_self_favorites(self, request, queryset):
        for obj in queryset:
            user_wallet, created = UserWallet.objects.get_or_create(user=request.user, wallet_id=obj.id)
            user_wallet.is_favorite = True
            user_wallet.save()

    @action(description="Убрать из избранных")
    def remove_wallets_from_self_favorites(self, request, queryset):
        for obj in queryset:
            user_wallet, created = UserWallet.objects.get_or_create(user=request.user, wallet_id=obj.id)
            user_wallet.is_favorite = False
            user_wallet.save()

    @action(
        description=_("Статистика"),
        url_path="changelist-wallet-open-stats",
        attrs={"target": "_blank"}
    )
    def open_stats(self, request: HttpRequest, object_id: int):
        obj = self.model.objects.get(pk=object_id)
        # Формируем корректный URL с помощью reverse
        new_url = reverse(
            'admin:solana_walletbuypricegt15k_changelist'
        ) + f"{obj.address}/statistics/"
        return redirect(new_url)

    @action(
        description=_("Открыть на GMGN"),
        url_path="changelist-wallet-open-gmgn",
        attrs={"target": "_blank"}
    )
    def open_gmgn(self, request: HttpRequest, object_id: int):
        obj = self.model.objects.get(pk=object_id)
        wallet_address = obj.address  # Если поле называется `address`
        return redirect(
            f"https://gmgn.ai/sol/address/{wallet_address}"
        )

    @action(
        description=_("Открыть на Cielo"),
        url_path="changelist-wallet-open-cielo",
        attrs={"target": "_blank"}
    )
    def open_cielo(self, request: HttpRequest, object_id: int):
        obj = self.model.objects.get(pk=object_id)
        wallet_address = obj.address  # Если поле называется `address`
        return redirect(
            f"https://app.cielo.finance/profile/{wallet_address}"
        )

    @action(
        description=_("Открыть на Solscan"),
        url_path="changelist-wallet-open-solscan",
        attrs={"target": "_blank"}
    )
    def open_solscan(self, request: HttpRequest, object_id: int):
        obj = self.model.objects.get(pk=object_id)
        wallet_address = obj.address  # Если поле называется `address`
        return redirect(
            f"https://solscan.io/account/{wallet_address}"
        )

    @display(
        description=_("Кошелек"),
        ordering="-address",
    )
    def wallet_display(self, obj):
        copy_button = render_to_string(
            'admin/copy_button.html',
            {
                'copy_value': obj.address,
            }  # передаем нужные данные в контекст
        )
        value = f'''
                    <div class="flex gap-1 font-semibold text-font-default-light dark:text-font-default-dark">
                        <a href="{obj.get_absolute_url()} " title="{obj.address}" target="_blank">{obj.address[:5]}...{obj.address[-2:]}</a>
                        <span class="text-font-subtle-light dark:text-font-subtle-dark">{copy_button}</span>
                    </div>
                '''
        return mark_safe(value)

    @display(
        description=_("Обн"),
        ordering="-last_stats_check",
    )
    def last_update_display(self, obj):
        last_stats_update_title = obj.last_stats_check
        last_stats_update_value = formatted_duration(now() - obj.last_stats_check) + " назад" if obj.last_stats_check else '-'
        value = f'''
                <div>
                    <p class="text-base " title="{ last_stats_update_title }" class="text-base text-sm text-font-subtle-light dark:text-font-subtle-dark">{ last_stats_update_value }</p>
                </div>
                '''
        return mark_safe(value)


    @display(
        description=_("Баланс"),
        ordering="-sol_balance",
    )
    def sol_balance_display(self, obj):
        value = round_to_first_non_zero(obj.details.sol_balance)
        return f'{value} SOL' if value else '0.00 SOL'

    @display(
        description=_("В/р Все"),
        ordering="-stats_buy_price_gt_15k_all__winrate",
        label=DISPLAY_LABELS,
    )
    def winrate_all_display(self, obj):
        if obj.stats_buy_price_gt_15k_all.winrate is None:
            return None
        value = round(obj.stats_buy_price_gt_15k_all.winrate, 2)
        return 'good' if value >= 50 else 'bad', f'{value} %'

    @display(
        description=_("Профит $"),
        ordering="-stats_buy_price_gt_15k_all__total_profit_usd",
    )
    def total_profit_usd_all_display(self, obj):
        value = obj.stats_buy_price_gt_15k_all.total_profit_usd
        if not value:
            return None
        return formatted_number(value, suffix=' $', add_sign=True)

    @display(
        description=_("Профит %"),
        ordering="-stats_buy_price_gt_15k_all__total_profit_multiplier",
        label=DISPLAY_LABELS,
    )
    def total_profit_multiplier_all_display(self, obj):
        value = obj.stats_buy_price_gt_15k_all.total_profit_multiplier
        if not value:
            return None
        return 'good' if value >= 1 else 'ok' if value >= 0 else 'bad', formatted_number(value, suffix=' %', add_sign=True)

    @display(
        description=_("Токенов"),
        ordering="-stats_buy_price_gt_15k_all__total_token",
    )
    def total_token_all_display(self, obj):
        return obj.stats_buy_price_gt_15k_all.total_token

    @display(
        description=_("<-50"),
        ordering="-stats_buy_price_gt_15k_all__pnl_lt_minus_dot5_percent",
        label=DISPLAY_LABELS,
    )
    def pnl_lt_minus_dot5_num_all_display(self, obj):
        value = obj.stats_buy_price_gt_15k_all.pnl_lt_minus_dot5_percent
        return 'bad', formatted_number(value, decimals=1, zero_value='-', suffix=" %")

    @display(
        description=_("0 - -50"),
        ordering="-stats_buy_price_gt_15k_all__pnl_minus_dot5_0x_percent",
        label=DISPLAY_LABELS,
    )
    def pnl_minus_dot5_0x_num_all_display(self, obj):
        value = obj.stats_buy_price_gt_15k_all.pnl_minus_dot5_0x_percent
        return 'bad', formatted_number(value, decimals=1, zero_value='-', suffix=" %")

    @display(
        description=_("0 - 200"),
        ordering="-stats_buy_price_gt_15k_all__pnl_lt_2x_percent",
        label=DISPLAY_LABELS,
    )
    def pnl_lt_2x_num_all_display(self, obj):
        value = obj.stats_buy_price_gt_15k_all.pnl_lt_2x_percent
        return 'good', formatted_number(value, decimals=1, zero_value='-', suffix=" %")

    @display(
        description=_("200 - 500"),
        ordering="-stats_buy_price_gt_15k_all__pnl_2x_5x_percent",
        label=DISPLAY_LABELS,
    )
    def pnl_2x_5x_num_all_display(self, obj):
        value = obj.stats_buy_price_gt_15k_all.pnl_2x_5x_percent
        return 'good', formatted_number(value, decimals=1, zero_value='-', suffix=" %")

    @display(
        description=_(">500"),
        ordering="-stats_buy_price_gt_15k_all__pnl_gt_5x_percent",
        label=DISPLAY_LABELS,
    )
    def pnl_gt_5x_num_all_display(self, obj):
        value = obj.stats_buy_price_gt_15k_all.pnl_gt_5x_percent
        return 'good', formatted_number(value, decimals=1, zero_value='-', suffix=" %")

    @display(
        description=_("Ср. пок."),
        ordering="-stats_buy_price_gt_15k_all__token_avg_buy_amount",
    )
    def token_avg_buy_amount_all_display(self, obj):
        value = obj.stats_buy_price_gt_15k_all.token_avg_buy_amount
        median = obj.stats_buy_price_gt_15k_all.token_median_buy_amount
        if not value:
            return None
        return formatted_number(value, suffix=' $')  # + f" ({formatted_number(median, suffix=' $')})"

    @display(
        description=_("Холд мед."),
        ordering="-stats_buy_price_gt_15k_all__token_buy_sell_duration_median",
        label=DISPLAY_LABELS,
    )
    def token_buy_sell_duration_median_all_display(self, obj):
        value = obj.stats_buy_price_gt_15k_all.token_buy_sell_duration_median
        return ('ok' if value > 30 else 'warning' if value > 5 else 'bad', formatted_duration(value)) if value is not None else None

    @display(
        description=_("Ср. профит"),
        ordering="-stats_buy_price_gt_15k_all__token_avg_profit_usd",
    )
    def token_avg_profit_usd_all_display(self, obj):
        value = obj.stats_buy_price_gt_15k_all.token_avg_profit_usd
        if not value:
            return None
        return formatted_number(value, suffix=' $', add_sign=True)

    @display(
        description=_("Сред ц.1п"),
        ordering="-stats_buy_price_gt_15k_all__token_first_buy_median_price_usd",
    )
    def token_first_buy_median_price_usd_all_display(self, obj):
        value = obj.stats_buy_price_gt_15k_all.token_first_buy_median_price_usd
        return formatted_number(value, decimals=10, suffix=" $", subscript=True)

    @display(
        description=_("Винрейт"),
        ordering="-stats_buy_price_gt_15k_30d__winrate",
        label=DISPLAY_LABELS,
    )
    def winrate_30d_display(self, obj):
        if obj.stats_buy_price_gt_15k_30d.winrate is None:
            return None
        value = round(obj.stats_buy_price_gt_15k_30d.winrate, 2)
        return 'good' if value >= 50 else 'bad', f'{value} %'

    @display(
        description=_("Профит $"),
        ordering="-stats_buy_price_gt_15k_30d__total_profit_usd",
    )
    def total_profit_usd_30d_display(self, obj):
        value = obj.stats_buy_price_gt_15k_30d.total_profit_usd
        if not value:
            return None
        return formatted_number(value, suffix=' $')

    @display(
        description=_("Профит %"),
        ordering="-stats_buy_price_gt_15k_30d__total_profit_multiplier",
        label=DISPLAY_LABELS,
    )
    def total_profit_multiplier_30d_display(self, obj):
        value = obj.stats_buy_price_gt_15k_30d.total_profit_multiplier
        if not value:
            return None
        return 'good' if value >= 1 else 'ok' if value >= 0 else 'bad', formatted_number(value, suffix=' %')

    @display(
        description=_("Токенов"),
        ordering="-stats_buy_price_gt_15k_30d__total_token",
    )
    def total_token_30d_display(self, obj):
        return obj.stats_buy_price_gt_15k_30d.total_token

    @display(
        description=_("<-50"),
        ordering="-stats_buy_price_gt_15k_30d__pnl_lt_minus_dot5_percent",
        label=DISPLAY_LABELS,
    )
    def pnl_lt_minus_dot5_num_30d_display(self, obj):
        value = obj.stats_buy_price_gt_15k_30d.pnl_lt_minus_dot5_percent
        return 'bad', formatted_number(value, decimals=1, zero_value='-', suffix=" %")

    @display(
        description=_("0 - -50"),
        ordering="-stats_buy_price_gt_15k_30d__pnl_minus_dot5_0x_percent",
        label=DISPLAY_LABELS,
    )
    def pnl_minus_dot5_0x_num_30d_display(self, obj):
        value = obj.stats_buy_price_gt_15k_30d.pnl_minus_dot5_0x_percent
        return 'bad', formatted_number(value, decimals=1, zero_value='-', suffix=" %")

    @display(
        description=_("0 - 200"),
        ordering="-stats_buy_price_gt_15k_30d__pnl_lt_2x_percent",
        label=DISPLAY_LABELS,
    )
    def pnl_lt_2x_num_30d_display(self, obj):
        value = obj.stats_buy_price_gt_15k_30d.pnl_lt_2x_percent
        return 'good', formatted_number(value, decimals=1, zero_value='-', suffix=" %")

    @display(
        description=_("200 - 500"),
        ordering="-stats_buy_price_gt_15k_30d__pnl_2x_5x_percent",
        label=DISPLAY_LABELS,
    )
    def pnl_2x_5x_num_30d_display(self, obj):
        value = obj.stats_buy_price_gt_15k_30d.pnl_2x_5x_percent
        return 'good', formatted_number(value, decimals=1, zero_value='-', suffix=" %")

    @display(
        description=_(">500"),
        ordering="-stats_buy_price_gt_15k_30d__pnl_gt_5x_percent",
        label=DISPLAY_LABELS,
    )
    def pnl_gt_5x_num_30d_display(self, obj):
        value = obj.stats_buy_price_gt_15k_30d.pnl_gt_5x_percent
        return 'good', formatted_number(value, decimals=1, zero_value='-', suffix=" %")

    @display(
        description=_("Ср. покупка"),
        ordering="-stats_buy_price_gt_15k_30d__token_avg_buy_amount",
    )
    def token_avg_buy_amount_30d_display(self, obj):
        value = obj.stats_buy_price_gt_15k_30d.token_avg_buy_amount
        median = obj.stats_buy_price_gt_15k_30d.token_median_buy_amount
        if not value:
            return None
        return formatted_number(value, suffix=' $')  # + f" ({formatted_number(median, suffix=' $')})"

    @display(
        description=_("Холд мед."),
        ordering="-stats_buy_price_gt_15k_30d__token_buy_sell_duration_median",
        label=DISPLAY_LABELS,
    )
    def token_buy_sell_duration_median_30d_display(self, obj):
        value = obj.stats_buy_price_gt_15k_30d.token_buy_sell_duration_median
        return ('ok' if value > 30 else 'warning' if value > 5 else 'bad', formatted_duration(value)) if value else None

    @display(
        description=_("Ср. профит"),
        ordering="-stats_buy_price_gt_15k_30d__token_avg_profit_usd",
    )
    def token_avg_profit_usd_30d_display(self, obj):
        value = obj.stats_buy_price_gt_15k_30d.token_avg_profit_usd
        if not value:
            return None
        return formatted_number(value, suffix=' $')

    @display(
        description=_("Сред ц.1п"),
        ordering="-stats_buy_price_gt_15k_30d__token_first_buy_median_price_usd",
    )
    def token_first_buy_median_price_usd_30d_display(self, obj):
        value = obj.stats_buy_price_gt_15k_30d.token_first_buy_median_price_usd
        return formatted_number(value, decimals=10, suffix=" $", subscript=True)

    @display(
        description=_("Винрейт"),
        ordering="-stats_buy_price_gt_15k_7d__winrate",
        label=DISPLAY_LABELS,
    )
    def winrate_7d_display(self, obj):
        if obj.stats_buy_price_gt_15k_7d.winrate is None:
            return None
        value = round(obj.stats_buy_price_gt_15k_7d.winrate, 2)
        return 'good' if value >= 50 else 'bad', f'{value} %'

    @display(
        description=_("Профит $"),
        ordering="-stats_buy_price_gt_15k_7d__total_profit_usd",
    )
    def total_profit_usd_7d_display(self, obj):
        value = obj.stats_buy_price_gt_15k_7d.total_profit_usd
        if not value:
            return None
        return formatted_number(value, suffix=' $')

    @display(
        description=_("Профит %"),
        ordering="-stats_buy_price_gt_15k_7d__total_profit_multiplier",
        label=DISPLAY_LABELS,
    )
    def total_profit_multiplier_7d_display(self, obj):
        value = obj.stats_buy_price_gt_15k_7d.total_profit_multiplier
        if not value:
            return None
        return 'good' if value >= 1 else 'ok' if value >= 0 else 'bad', formatted_number(value, suffix=' %')

    @display(
        description=_("Токенов"),
        ordering="-stats_buy_price_gt_15k_7d__total_token",
    )
    def total_token_7d_display(self, obj):
        return obj.stats_buy_price_gt_15k_7d.total_token

    @display(
        description=_("<-50"),
        ordering="-stats_buy_price_gt_15k_7d__pnl_lt_minus_dot5_percent",
        label=DISPLAY_LABELS,
    )
    def pnl_lt_minus_dot5_num_7d_display(self, obj):
        value = obj.stats_buy_price_gt_15k_7d.pnl_lt_minus_dot5_percent
        return 'bad', formatted_number(value, decimals=1, zero_value='-', suffix=" %")

    @display(
        description=_("0 - -50"),
        ordering="-stats_buy_price_gt_15k_7d__pnl_minus_dot5_0x_percent",
        label=DISPLAY_LABELS,
    )
    def pnl_minus_dot5_0x_num_7d_display(self, obj):
        value = obj.stats_buy_price_gt_15k_7d.pnl_minus_dot5_0x_percent
        return 'bad', formatted_number(value, decimals=1, zero_value='-', suffix=" %")

    @display(
        description=_("0 - 200"),
        ordering="-stats_buy_price_gt_15k_7d__pnl_lt_2x_percent",
        label=DISPLAY_LABELS,
    )
    def pnl_lt_2x_num_7d_display(self, obj):
        value = obj.stats_buy_price_gt_15k_7d.pnl_lt_2x_percent
        return 'good', formatted_number(value, decimals=1, zero_value='-', suffix=" %")

    @display(
        description=_("200 - 500"),
        ordering="-stats_buy_price_gt_15k_7d__pnl_2x_5x_percent",
        label=DISPLAY_LABELS,
    )
    def pnl_2x_5x_num_7d_display(self, obj):
        value = obj.stats_buy_price_gt_15k_7d.pnl_2x_5x_percent
        return 'good', formatted_number(value, decimals=1, zero_value='-', suffix=" %")

    @display(
        description=_(">500"),
        ordering="-stats_buy_price_gt_15k_7d__pnl_gt_5x_percent",
        label=DISPLAY_LABELS,
    )
    def pnl_gt_5x_num_7d_display(self, obj):
        value = obj.stats_buy_price_gt_15k_7d.pnl_gt_5x_percent
        return 'good', formatted_number(value, decimals=1, zero_value='-', suffix=" %")

    @display(
        description=_("Ср. покупка"),
        ordering="-stats_buy_price_gt_15k_7d__token_avg_buy_amount",
    )
    def token_avg_buy_amount_7d_display(self, obj):
        value = obj.stats_buy_price_gt_15k_7d.token_avg_buy_amount
        median = obj.stats_buy_price_gt_15k_7d.token_median_buy_amount
        if not value:
            return None
        return formatted_number(value, suffix=' $')  # + f" ({formatted_number(median, suffix=' $')})"

    @display(
        description=_("Холд мед."),
        ordering="-stats_buy_price_gt_15k_7d__token_buy_sell_duration_median",
        label=DISPLAY_LABELS,
    )
    def token_buy_sell_duration_median_7d_display(self, obj):
        value = obj.stats_buy_price_gt_15k_7d.token_buy_sell_duration_median
        return ('ok' if value > 30 else 'warning' if value > 5 else 'bad', formatted_duration(value)) if value else None  # + f" ({formatted_duration(median)})"

    @display(
        description=_("Ср. профит"),
        ordering="-stats_buy_price_gt_15k_7d__token_avg_profit_usd",
    )
    def token_avg_profit_usd_7d_display(self, obj):
        value = obj.stats_buy_price_gt_15k_7d.token_avg_profit_usd
        if not value:
            return None
        return formatted_number(value, suffix=' $')

    @display(
        description=_("Сред ц.1п"),
        ordering="-stats_buy_price_gt_15k_7d__token_first_buy_median_price_usd",
    )
    def token_first_buy_median_price_usd_7d_display(self, obj):
        value = obj.stats_buy_price_gt_15k_7d.token_first_buy_median_price_usd
        return formatted_number(value, decimals=10, suffix=" $", subscript=True)