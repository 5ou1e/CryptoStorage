from collections import defaultdict
from enum import StrEnum

from django.utils.translation import gettext_lazy as _
from solana.models import Token, WalletTokenStatistic
from unfold.contrib.filters.admin import (DropdownFilter, RangeNumericFilter,
                                          TextFilter)
from users.models import UserWallet


class WalletFilterType(StrEnum):
    IS_FAVORITE = "is_favorite"
    IS_WATCH_LATER = "is_watch_later"
    IS_BLACKLISTED = "is_blacklisted"
    IS_BOT = "is_bot"
    IS_SCAMMER = "is_scammer"


class PeriodFilter(DropdownFilter):
    title = _("Период")  # Название фильтра, отображаемое в админке
    parameter_name = "period"

    def lookups(self, request, model_admin):
        # Определяем доступные значения фильтра
        return [
            ("7d", _("За 7 дней")),
            ("30d", _("За 30 дней")),
            ("all", _("За все время")),
        ]

    def queryset(self, request, queryset):
        return queryset


class IsScammerFilter(DropdownFilter):
    title = _("Скамеркие кошельки")  # Название фильтра, отображаемое в админке
    parameter_name = WalletFilterType.IS_SCAMMER

    def lookups(self, request, model_admin):
        # Определяем доступные значения фильтра
        return [
            ("0", _("Кроме скамерских")),
            ("1", _("Скамерские")),
        ]

    def queryset(self, request, queryset):
        if self.value() == "0":
            return queryset.filter(is_scammer=False)
        if self.value() == "1":
            # Исключаем кошельки, которые находятся в черном списке
            return queryset.filter(is_scammer=True)
        return queryset


class IsBotFilter(DropdownFilter):
    title = _("Бот кошельки")  # Название фильтра, отображаемое в админке
    parameter_name = WalletFilterType.IS_BOT

    def lookups(self, request, model_admin):
        # Определяем доступные значения фильтра
        return [
            ("0", _("Кроме ботов")),
            ("1", _("Боты")),
        ]

    def queryset(self, request, queryset):
        if self.value() == "0":
            return queryset.filter(is_bot=False)
        if self.value() == "1":
            # Исключаем кошельки, которые находятся в черном списке
            return queryset.filter(is_bot=True)
        return queryset


class UserWalletFilter(DropdownFilter):
    """Базовый фильтр для связи с UserWallet"""

    user_wallet_field = None  # Должно быть переопределено в наследниках
    title = None  # Должно быть переопределено в наследниках
    parameter_name = None  # Должно быть переопределено в наследниках

    def lookups(self, request, model_admin):
        return (
            ("1", self.title),
            ("0", _(f"Кроме {self.title.lower()}")),
        )

    def queryset(self, request, queryset):
        if not self.user_wallet_field:
            return queryset

        user = request.user
        filtered_wallet_ids = UserWallet.objects.filter(
            user_id=user.id, **{self.user_wallet_field: True}
        ).values_list("wallet_id", flat=True)

        if self.value() == "1":
            return queryset.filter(id__in=filtered_wallet_ids)
        elif self.value() == "0":
            return queryset.exclude(id__in=filtered_wallet_ids)

        return queryset


class IsFavoriteFilter(UserWalletFilter):
    title = _("Избранные")
    parameter_name = WalletFilterType.IS_FAVORITE
    user_wallet_field = WalletFilterType.IS_FAVORITE


class IsWatchLaterFilter(UserWalletFilter):
    title = _("Смотреть позже")
    parameter_name = WalletFilterType.IS_WATCH_LATER
    user_wallet_field = WalletFilterType.IS_WATCH_LATER


class IsBlacklistedFilter(UserWalletFilter):
    title = _("Блеклист")
    parameter_name = WalletFilterType.IS_BLACKLISTED
    user_wallet_field = WalletFilterType.IS_BLACKLISTED


class GenericRangeFilter(RangeNumericFilter):

    BASE_KEYS = {
        "winrate": "Винрейт",
        "total_profit_usd": "Профит в USD",
        "total_profit_multiplier": "Профит в %",
        "total_token": "Токенов",
        "token_avg_buy_amount": "Ср. сумма покупки 1 токена",
        "token_avg_profit_usd": "Ср. профит с токена в USD",
        "pnl_gt_5x_percent": "% Токенов с профитом > 500%",
        "token_first_buy_median_price_usd": "Средняя цена 1й покупки",
        "token_buy_sell_duration_median": "Медиана времени 1-ой покупки-продажи (в секундах)",
    }

    PREFIXES = {
        "": "",
        "stats_7d__": "7️⃣ ",
        "stats_30d__": "3️⃣0️⃣ ",
        "stats_all__": "",
        "stats_buy_price_gt_15k_all__": "",
        "stats_buy_price_gt_15k_7d__": "7️⃣ ",
        "stats_buy_price_gt_15k_30d__": "3️⃣0️⃣ ",
    }

    DIRECT_NAMES = {
        "sol_balance": "SOL Баланс",
    }

    def __init__(self, field, request, params, model, model_admin, field_path=None):
        super().__init__(field, request, params, model, model_admin, field_path)
        self.title = self.get_title()

    def get_title(self):
        if self.field_path in self.DIRECT_NAMES:
            return self.DIRECT_NAMES[self.field_path]

        for prefix, prefix_value in self.PREFIXES.items():
            if self.field_path.startswith(prefix):
                base_key = self.field_path[len(prefix) :]
                if base_key in self.BASE_KEYS:
                    return f"{prefix_value}{self.BASE_KEYS[base_key]}"

        return self.field_path


class TokensIntersectionFilter(TextFilter):
    title = _("С токенами (Адреса токенов через запятую)")
    parameter_name = "tokens_intersection"

    def lookups(self, request, model_admin):
        return []

    def queryset(self, request, queryset):
        token_addresses = self.value()  # Получаем выбранные токены
        if not token_addresses:
            return queryset
        # Разделяем введенные адреса через запятую
        token_addresses = {token.strip() for token in token_addresses.split(",")}
        token_ids = Token.objects.filter(address__in=token_addresses).values_list("id")
        # Шаг 1: Достаём все активности в виде списка wallet_id и token_id
        activities = list(
            WalletTokenStatistic.objects.filter(token__id__in=token_ids).values_list(
                "wallet_id", "token__id"
            )
        )

        # Шаг 2: Создаём маппинг wallet_id -> set(token_ids)
        wallet_to_tokens = defaultdict(set)
        for wallet_id, token_id in activities:
            wallet_to_tokens[wallet_id].add(token_id)

        # Шаг 3: Определяем кошельки, которые связаны со всеми искомыми токенами
        valid_wallet_ids = [
            wallet_id
            for wallet_id, token_ids in wallet_to_tokens.items()
            if len(token_ids)
            == len(token_addresses)  # Все токены должны присутствовать
        ]

        # Шаг 4: Фильтруем основной queryset по найденным wallet_ids
        queryset = queryset.filter(id__in=valid_wallet_ids)
        # print(str(queryset.query))
        return queryset
