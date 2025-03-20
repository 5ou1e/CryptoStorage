from django.contrib import admin
from django.templatetags.static import static
from django.utils.html import mark_safe
from django.utils.translation import gettext_lazy as _
from solana.models import Token, TokenPrice
from unfold.admin import ModelAdmin
from unfold.contrib.filters.admin import FieldTextFilter
from unfold.decorators import display

from ..shared.misc import LargeTablePaginator
from .inlines import WalletTokenStatisticInline


@admin.register(Token)
class TokenAdmin(ModelAdmin):
    inlines = [WalletTokenStatisticInline]
    list_per_page = 30
    show_full_result_count = False
    paginator = LargeTablePaginator
    readonly_fields = ('created_at', 'updated_at')
    list_display = ('logo_display', 'symbol', 'address', 'created_at')
    list_display_links = ('logo_display', 'symbol', 'address',)
    search_fields = ('address', 'symbol')
    list_filter_submit = True  # Submit button at the bottom of the filter
    compressed_fields = True
    list_filter = [
        ("address", FieldTextFilter),
        ("name", FieldTextFilter),
    ]

    @display(description=_("Лого"))
    def logo_display(self, obj):
        default_logo_url = static('img/logo.png')
        logo_url = obj.logo if obj.logo else default_logo_url

        return mark_safe(
            f'''<img src="{logo_url}" onerror="this.onerror=null;this.src='{default_logo_url}';" style="width: 40px; height: 40px; border-radius: 50%; object-fit: cover;" />''',
        )


@admin.register(TokenPrice)
class TokenPriceAdmin(ModelAdmin):
    autocomplete_fields = ['token']
    paginator = LargeTablePaginator
    list_display = ['token__symbol', 'price_usd', 'minute']
    list_display_links = ['token__symbol', 'minute']


