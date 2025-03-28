from django.db.models import F
from django.utils.translation import gettext_lazy as _
from unfold.contrib.filters.admin import DropdownFilter


class IsTokenSellAmountGtBuyAmountFilter(DropdownFilter):
    title = _("Сумма продаж > суммы покупок (в единицах токена)")
    parameter_name = "is_token_sell_amount_gt_buy_amount"

    def lookups(self, request, model_admin):
        return [
            ["0", _("Нет")],
            ["1", _("Да")],
        ]

    def queryset(self, request, queryset):
        if self.value() == "1":
            return queryset.filter(
                total_sell_amount_token__gt=F("total_buy_amount_token") * 1.01,
                total_buys_count__gt=0,
            )
        if self.value() == "0":
            return queryset.exclude(
                total_sell_amount_token__gt=F("total_buy_amount_token") * 1.01,
                total_buys_count__gt=0,
            )

        return queryset
