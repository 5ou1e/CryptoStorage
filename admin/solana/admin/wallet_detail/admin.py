from django.contrib import admin
from solana.models import WalletDetail
from unfold.admin import ModelAdmin

from ..shared.misc import LargeTablePaginator


@admin.register(WalletDetail)
class WalletDetailAdmin(ModelAdmin):
    inlines = []
    show_full_result_count = False
    paginator = LargeTablePaginator
    autocomplete_fields = ['wallet']
    list_display = ('id', 'wallet__address')
    list_display_links = ('wallet__address',)
    search_fields = ('wallet__address__exact',)
    list_filter_submit = True  # Submit button at the bottom of the filter
