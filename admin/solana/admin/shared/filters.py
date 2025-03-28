from django.core.validators import EMPTY_VALUES
from django.db.models import Subquery
from unfold.contrib.filters.admin import TextFilter

from solana.models import Token, Wallet


class WalletAddressFilter(TextFilter):
    title = "Кошелек"
    parameter_name = "wallet_address"

    def queryset(self, request, queryset):
        if self.value() not in EMPTY_VALUES:
            # Here write custom query
            wallet_subquery = Wallet.objects.filter(address=self.value()).values("id")[
                :1
            ]
            return queryset.filter(wallet_id=Subquery(wallet_subquery))
        return queryset


class TokenAddressFilter(TextFilter):
    title = "Токен"
    parameter_name = "token_address"

    def queryset(self, request, queryset):
        if self.value() not in EMPTY_VALUES:
            # Here write custom query
            wallet_subquery = Token.objects.filter(address=self.value()).values("id")[
                :1
            ]
            return queryset.filter(token_id=Subquery(wallet_subquery))
        return queryset
