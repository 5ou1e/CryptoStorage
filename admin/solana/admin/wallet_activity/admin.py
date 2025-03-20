from django.contrib import admin
from solana.models import WalletActivity
from unfold.admin import ModelAdmin
from unfold.contrib.filters.admin import FieldTextFilter

from ..shared.misc import LargeTablePaginator


@admin.register(WalletActivity)
class WalletActivityAdmin(ModelAdmin):
    inlines = []
    list_per_page = 30
    show_full_result_count = False
    paginator = LargeTablePaginator
    autocomplete_fields = ['token', 'wallet']
    readonly_fields = ('created_at', 'updated_at',)
    list_display = ['tx_hash', 'wallet__address', 'token__address', 'event_type', 'token_amount', ]  # + [field.name for field in GmgnWalletActivity._meta.get_fields()]
    list_display_links = ['tx_hash', 'wallet__address', 'token__address',]
    search_fields = ('token__name', 'wallet__address__exact', 'token__address__exact', 'tx_hash__exact')
    compressed_fields = True
    list_filter_submit = True  # Submit button at the bottom of the filter
    list_filter = [
        ("wallet__address", FieldTextFilter),
        ("token__address", FieldTextFilter),
        ("tx_hash", FieldTextFilter),
    ]
    list_fullwidth = True
    list_horizontal_scrollbar_top = True

