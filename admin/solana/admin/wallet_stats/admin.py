from django.contrib import admin
from solana.models import (WalletPeriodStatistic7d, WalletPeriodStatistic30d,
                           WalletPeriodStatisticAll)
from unfold.admin import ModelAdmin


@admin.register(WalletPeriodStatistic7d)
class WalletPeriodStatistic7dAdmin(ModelAdmin):
    search_fields = ('wallet__address',)


@admin.register(WalletPeriodStatistic30d)
class WalletPeriodStatistic30dAdmin(ModelAdmin):
    search_fields = ('wallet__address',)


@admin.register(WalletPeriodStatisticAll)
class WalletPeriodStatisticAllAdmin(ModelAdmin):
    search_fields = ('wallet__address',)
