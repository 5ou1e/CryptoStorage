from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from django.urls import path
from unfold.admin import ModelAdmin
from unfold.contrib.filters.admin import FieldTextFilter, RangeDateTimeFilter

from .admin_views import (toggle_wallet_status, update_remark,
                          update_wallet_stats_view)
from .models import User, UserWallet

admin.site.unregister(Group)


@admin.register(User)
class CustomUserAdmin(BaseUserAdmin, ModelAdmin):
    list_filter_submit = True  # Submit button at the bottom of the filter
    list_filter = [("username", FieldTextFilter), ("date_joined", RangeDateTimeFilter)]
    search_fields = ("id", "username", "email")


@admin.register(Group)
class GroupAdmin(BaseGroupAdmin, ModelAdmin):
    pass


@admin.register(UserWallet)
class UserWalletAdmin(ModelAdmin):
    inlines = []
    list_display = ("id", "user_id", "wallet_id")

    def get_urls(self):
        return [
            path(
                "<uuid:wallet_id>/toggle_status/",
                toggle_wallet_status,  # IMPORTANT: model_admin is required
                name="user_wallet_toggle_status",
            ),
            path(
                "<uuid:wallet_id>/update_remark/",
                update_remark,  # IMPORTANT: model_admin is required
                name="user_wallet_update_remark",
            ),
            path(
                "<uuid:wallet_id>/update_stats/",
                update_wallet_stats_view,  # IMPORTANT: model_admin is required
                name="wallet_update_stats",
            ),
        ] + super().get_urls()
