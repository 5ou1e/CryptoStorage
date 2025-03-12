from collections import defaultdict

from django.utils.translation import gettext_lazy as _
from solana.models import Token, WalletTokenStatistic
from unfold.contrib.filters.admin import (
    DropdownFilter,
    RangeNumericFilter,
    TextFilter,
)
from users.models import UserWallet


class PeriodFilter(DropdownFilter):
    title = _('Период')  # Название фильтра, отображаемое в админке
    parameter_name = 'period'

    def lookups(self, request, model_admin):
        # Определяем доступные значения фильтра
        return [
            ('7d', _('За 7 дней')),
            ('30d', _('За 30 дней')),
            ('all', _('За все время')),
        ]

    def queryset(self, request, queryset):
        return queryset


class IsScammerFilter(DropdownFilter):
    title = _('Скамеркие кошельки')  # Название фильтра, отображаемое в админке
    parameter_name = 'is_scammer'

    def lookups(self, request, model_admin):
        # Определяем доступные значения фильтра
        return [
            ('0', _('Кроме скамерских')),
            ('1', _('Скамерские')),
        ]

    def queryset(self, request, queryset):
        if self.value() == '0':
            return queryset.filter(details__is_scammer=False)
        if self.value() == '1':
            # Исключаем кошельки, которые находятся в черном списке
            return queryset.filter(details__is_scammer=True)
        return queryset


class IsBotFilter(DropdownFilter):
    title = _('Бот кошельки')  # Название фильтра, отображаемое в админке
    parameter_name = 'is_bot'

    def lookups(self, request, model_admin):
        # Определяем доступные значения фильтра
        return [
            ('0', _('Кроме ботов')),
            ('1', _('Боты')),
        ]

    def queryset(self, request, queryset):
        if self.value() == '0':
            return queryset.filter(details__is_bot=False)
        if self.value() == '1':
            # Исключаем кошельки, которые находятся в черном списке
            return queryset.filter(details__is_bot=True)
        return queryset


class IsFavoriteFilter(DropdownFilter):
    title = _('Избранные')  # Заголовок фильтра
    parameter_name = 'is_my_favorite'  # Название параметра в URL

    def lookups(self, request, model_admin):
        return (
            ('1', _('Избранные')),  # Параметры фильтра
            ('0', _('Кроме избранных')),
        )

    def queryset(self, request, queryset):
        user = request.user
        if self.value() == '1':
            return queryset.filter(
                userwallet__user=user,  # связь с моделью UserWallet через внешний ключ user
                userwallet__is_favorite=True  # фильтрация по избранному кошельку
            )
        if self.value() == '0':
            return queryset.exclude(
                userwallet__is_favorite=True  # исключение избранных кошельков
            )
        return queryset


class IsWatchLaterFilter(DropdownFilter):
    title = _('Смотреть позже')  # Заголовок фильтра
    parameter_name = 'is_watch_later'  # Название параметра в URL

    def lookups(self, request, model_admin):
        return (
            ('1', _('Смотреть позже')),  # Параметры фильтра
            ('0', _('Кроме')),
        )

    def queryset(self, request, queryset):
        user = request.user
        if self.value() == '1':
            return queryset.filter(
                userwallet__user=user,  # связь с моделью UserWallet через внешний ключ user
                userwallet__is_watch_later=True  # фильтрация по избранному кошельку
            )
        if self.value() == '0':
            return queryset.exclude(
                userwallet__is_watch_later=True  # исключение избранных кошельков
            )
        return queryset


class IsBlacklistedFilter(DropdownFilter):
    title = _('Блеклист')  # Заголовок фильтра
    parameter_name = 'is_blacklisted'  # Название параметра в URL

    def lookups(self, request, model_admin):
        return (
            ('0', _('Кроме блеклиста')),
            ('1', _('Блеклист')),  # Параметры фильтра
        )

    def queryset(self, request, queryset):
        user = request.user
        if self.value() in ['1', '0']:  # Проверяем, если фильтр активен
            # Получаем все ID кошельков с нужным пользователем и флагом is_blacklisted
            blacklisted_wallet_ids = UserWallet.objects.filter(
                user_id=user.id,
                is_blacklisted=True
            ).values_list('wallet_id', flat=True)
            if self.value() == '1':
                # Фильтруем основной queryset, используя только полученные ID кошельков
                return queryset.filter(id__in=blacklisted_wallet_ids)

            if self.value() == '0':
                # Исключаем кошельки, которые находятся в черном списке
                return queryset.exclude(id__in=blacklisted_wallet_ids)

        return queryset


class CustomRangeFilter(RangeNumericFilter):
    def __init__(self, field, request, params, model, model_admin, field_path=None):
        super().__init__(field, request, params, model, model_admin, field_path)
        self.title = self.get_custom_title()

    def get_custom_title(self):
        custom_titles = {
            "details__sol_balance": "SOL Баланс",


            "stats_all__winrate": "Винрейт",
            "stats_all__total_profit_usd": "Профит в USD",
            "stats_all__total_profit_multiplier": "Профит в %",
            "stats_all__total_token": "Токенов",
            "stats_all__token_avg_buy_amount": "Ср. сумма покупки 1 токена",
            "stats_all__token_avg_profit_usd": "Ср. профит с токена в USD",
            "stats_all__pnl_gt_5x_percent": "% Токенов с профитом > 500%",
            "stats_all__token_first_buy_median_price_usd": "Средняя цена 1й покупки",
            "stats_all__token_buy_sell_duration_median": "Медиана времени 1-ой покупки-продажи в секундах",

            "stats_7d__winrate": "7️⃣ Винрейт",
            "stats_7d__total_profit_usd": "7️⃣ Профит в USD",
            "stats_7d__total_profit_multiplier": "7️⃣ Профит в %",
            "stats_7d__total_token": "7️⃣ Токенов",
            "stats_7d__token_avg_buy_amount": "7️⃣ Ср. сумма покупки 1 токена",
            "stats_7d__token_avg_profit_usd": "7️⃣ Ср. профит с токена в USD",
            "stats_7d__pnl_gt_5x_percent": "7️⃣ % Токенов с профитом > 500%",
            "stats_7d__token_first_buy_median_price_usd": "7️⃣ Средняя цена 1й покупки",
            "stats_7d__token_buy_sell_duration_median": "7️⃣ Медиана времени 1-ой покупки-продажи в секундах",

            "stats_30d__winrate": "3️⃣0️⃣ Винрейт",
            "stats_30d__total_profit_usd": "3️⃣0️⃣ Профит в USD",
            "stats_30d__total_profit_multiplier": "3️⃣0️⃣ Профит в %",
            "stats_30d__total_token": "3️⃣0️⃣ Токенов",
            "stats_30d__token_avg_buy_amount": "3️⃣0️⃣ Ср. сумма покупки 1 токена",
            "stats_30d__token_avg_profit_usd": "3️⃣0️⃣ Ср. профит с токена в USD",
            "stats_30d__pnl_gt_5x_percent": "3️⃣0️⃣ % Токенов с профитом > 500%",
            "stats_30d__token_first_buy_median_price_usd": "3️⃣0️⃣ Средняя цена 1й покупки",
            "stats_30d__token_buy_sell_duration_median": "3️⃣0️⃣ Медиана времени 1-ой покупки-продажи в секунда",


            "stats_buy_price_gt_15k_all__winrate": "Винрейт",
            "stats_buy_price_gt_15k_all__total_profit_usd": "Профит в USD",
            "stats_buy_price_gt_15k_all__total_profit_multiplier": "Профит в %",
            "stats_buy_price_gt_15k_all__total_token": "Токенов",
            "stats_buy_price_gt_15k_all__token_avg_buy_amount": "Ср. сумма покупки 1 токена",
            "stats_buy_price_gt_15k_all__token_avg_profit_usd": "Ср. профит с токена в USD",
            "stats_buy_price_gt_15k_all__pnl_gt_5x_percent": "% Токенов с профитом > 500%",
            "stats_buy_price_gt_15k_all__token_first_buy_median_price_usd": "Средняя цена 1й покупки",
            "stats_buy_price_gt_15k_all__token_buy_sell_duration_median": "Медиана времени 1-ой покупки-продажи в секундах",

            "stats_buy_price_gt_15k_7d__winrate": "7️⃣ Винрейт",
            "stats_buy_price_gt_15k_7d__total_profit_usd": "7️⃣ Профит в USD",
            "stats_buy_price_gt_15k_7d__total_profit_multiplier": "7️⃣ Профит в %",
            "stats_buy_price_gt_15k_7d__total_token": "7️⃣ Токенов",
            "stats_buy_price_gt_15k_7d__token_avg_buy_amount": "7️⃣ Ср. сумма покупки 1 токена",
            "stats_buy_price_gt_15k_7d__token_avg_profit_usd": "7️⃣ Ср. профит с токена в USD",
            "stats_buy_price_gt_15k_7d__pnl_gt_5x_percent": "7️⃣ % Токенов с профитом > 500%",
            "stats_buy_price_gt_15k_7d__token_first_buy_median_price_usd": "7️⃣ Средняя цена 1й покупки",
            "stats_buy_price_gt_15k_7d__token_buy_sell_duration_median": "7️⃣ Медиана времени 1-ой покупки-продажи в секундах",

            "stats_buy_price_gt_15k_30d__winrate": "3️⃣0️⃣ Винрейт",
            "stats_buy_price_gt_15k_30d__total_profit_usd": "3️⃣0️⃣ Профит в USD",
            "stats_buy_price_gt_15k_30d__total_profit_multiplier": "3️⃣0️⃣ Профит в %",
            "stats_buy_price_gt_15k_30d__total_token": "3️⃣0️⃣ Токенов",
            "stats_buy_price_gt_15k_30d__token_avg_buy_amount": "3️⃣0️⃣ Ср. сумма покупки 1 токена",
            "stats_buy_price_gt_15k_30d__token_avg_profit_usd": "3️⃣0️⃣ Ср. профит с токена в USD",
            "stats_buy_price_gt_15k_30d__pnl_gt_5x_percent": "3️⃣0️⃣ % Токенов с профитом > 500%",
            "stats_buy_price_gt_15k_30d__token_first_buy_median_price_usd": "3️⃣0️⃣ Средняя цена 1й покупки",
            "stats_buy_price_gt_15k_30d__token_buy_sell_duration_median": "3️⃣0️⃣ Медиана времени 1-ой покупки-продажи в секунда",
        }
        return custom_titles.get(self.field_path, self.field_path)


class TokensIntersectionFilter(TextFilter):
    title = _("С токенами (Адреса токенов через запятую)")
    parameter_name = "tokens_intercection"

    def lookups(self, request, model_admin):
        return []

    def queryset(self, request, queryset):
        token_addresses = self.value()  # Получаем выбранные токены
        if not token_addresses:
            return queryset
        # Разделяем введенные адреса через запятую
        token_addresses = {token.strip() for token in token_addresses.split(',')}
        token_ids = Token.objects.filter(address__in=token_addresses).values_list('id')
        # Шаг 1: Достаём все активности в виде списка wallet_id и token_id
        activities = list(
            WalletTokenStatistic.objects.filter(
                token__id__in=token_ids
            ).values_list('wallet_id', 'token__id')
        )

        # Шаг 2: Создаём маппинг wallet_id -> set(token_ids)
        wallet_to_tokens = defaultdict(set)
        for wallet_id, token_id in activities:
            wallet_to_tokens[wallet_id].add(token_id)

        # Шаг 3: Определяем кошельки, которые связаны со всеми искомыми токенами
        valid_wallet_ids = [
            wallet_id
            for wallet_id, token_ids in wallet_to_tokens.items()
            if len(token_ids) == len(token_addresses)  # Все токены должны присутствовать
        ]

        # Шаг 4: Фильтруем основной queryset по найденным wallet_ids
        queryset = queryset.filter(id__in=valid_wallet_ids)
        # print(str(queryset.query))
        return queryset
