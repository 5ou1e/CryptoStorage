from unfold.admin import StackedInline, TabularInline

from solana.models import (WalletStatistic7d, WalletStatistic30d,
                           WalletStatisticAll, WalletTokenStatistic)

from ..common.misc import LimitModelFormset


class WalletTokenStatisticInline(TabularInline):
    verbose_name = "Wallet-Token"
    model = WalletTokenStatistic
    formset = LimitModelFormset
    readonly_fields = ("wallet", "token")
    autocomplete_fields = ("wallet", "token")
    max_num = 0
    tab = True


class WalletStatistic7dInline(StackedInline):
    model = WalletStatistic7d
    verbose_name = "Stats 7d"
    tab = True


class WalletStatistic30dInline(StackedInline):
    model = WalletStatistic30d
    verbose_name = "Stats 30d"
    tab = True


class WalletStatisticAllInline(StackedInline):
    model = WalletStatisticAll
    verbose_name = "Stats All Time"
    tab = True
