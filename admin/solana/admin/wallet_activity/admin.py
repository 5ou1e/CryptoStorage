from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from unfold.contrib.filters.admin import FieldTextFilter
from unfold.decorators import display

from ..common.base_admin_model import BaseAdminModel
from ..common.filters import TokenAddressFilter, WalletAddressFilter
from ...models import WalletActivity


@admin.register(WalletActivity)
class WalletActivityAdmin(BaseAdminModel):
    list_horizontal_scrollbar_top = True
    autocomplete_fields = ["token", "wallet"]
    readonly_fields = (
        "created_at",
        "updated_at",
    )
    list_display = [
        "tx_hash",
        "wallet_address_display",
        "token_address_display",
        "event_type",
        "token_amount",
    ]  # + [field.name for field in GmgnWalletActivity._meta.get_fields()]
    list_display_links = [
        "tx_hash",
        "wallet_address_display",
        "token_address_display",
    ]
    search_fields = (
        "token__name",
        "wallet__address__exact",
        "token__address__exact",
        "tx_hash__exact",
    )
    list_filter = [
        ("tx_hash", FieldTextFilter),
        WalletAddressFilter,
        TokenAddressFilter,
    ]

    @display(
        description=_("Кошелек"),
        ordering="-wallet__address",
    )
    def wallet_address_display(self, obj):
        return obj.wallet.address

    @display(
        description=_("Токен"),
        ordering="-token__address",
    )
    def token_address_display(self, obj):
        return obj.token.address
