from django.contrib import admin
from solana.models import WalletTokenStatistic
from unfold.admin import ModelAdmin
from unfold.contrib.filters.admin import FieldTextFilter

from ..shared.misc import LargeTablePaginator


@admin.register(WalletTokenStatistic)
class WalletTokenStatisticAdmin(ModelAdmin):
    list_per_page = 30
    show_full_result_count = False
    paginator = LargeTablePaginator
    autocomplete_fields = ['token', 'wallet']
    list_display = ['token__symbol', 'token__address', 'wallet__address', 'created_at', 'updated_at']
    list_display_links = ['token__symbol', 'token__address', 'wallet__address', ]
    search_fields = ['token__address__exact', 'wallet__address__exact', ]
    compressed_fields = True
    list_filter = [
        ("wallet__address", FieldTextFilter),
        ("token__address", FieldTextFilter),
    ]
    list_filter_submit = True
