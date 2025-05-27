from django.contrib import admin
from solana.admin.common.base_admin_model import BaseAdminModel
from solana.models import (WalletStatistic7d, WalletStatistic30d,
                           WalletStatisticAll)
from unfold.admin import ModelAdmin


# @admin.register(WalletStatistic7d)
class WalletStatistic7dAdmin(BaseAdminModel):
    search_fields = ("wallet__address",)


# @admin.register(WalletStatistic30d)
class WalletStatistic30dAdmin(BaseAdminModel):
    search_fields = ("wallet__address",)


# @admin.register(WalletStatisticAll)
class WalletStatisticAllAdmin(BaseAdminModel):
    search_fields = ("wallet__address",)
