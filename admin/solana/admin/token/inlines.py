from unfold.admin import TabularInline

from solana.models import WalletTokenStatistic

from ..shared.misc import LimitModelFormset


class WalletTokenStatisticInline(TabularInline):
    verbose_name = "Wallet-Token Stat"
    model = WalletTokenStatistic
    formset = LimitModelFormset
    readonly_fields = ("wallet", "token")
    autocomplete_fields = ("wallet", "token")
    max_num = 0
    tab = True
