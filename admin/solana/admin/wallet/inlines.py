from solana.models import (WalletPeriodStatistic7d,
                           WalletPeriodStatistic30d, WalletPeriodStatisticAll,
                           WalletTokenStatistic)
from unfold.admin import StackedInline, TabularInline

from ..shared.misc import LimitModelFormset


class WalletTokenStatisticInline(TabularInline):
    verbose_name = 'Wallet-Token Stat'
    model = WalletTokenStatistic
    formset = LimitModelFormset
    readonly_fields = ('wallet', 'token')
    autocomplete_fields = ('wallet', 'token')
    max_num = 0
    tab = True


class WalletPeriodStatistic7dInline(StackedInline):
    model = WalletPeriodStatistic7d
    verbose_name = 'Stats 7d'
    tab = True


class WalletPeriodStatistic30dInline(StackedInline):
    model = WalletPeriodStatistic30d
    verbose_name = 'Stats 30d'
    tab = True


class WalletPeriodStatisticAllInline(StackedInline):
    model = WalletPeriodStatisticAll
    verbose_name = 'Stats All Time'
    tab = True
