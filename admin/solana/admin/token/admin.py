from django.contrib import admin
from django.templatetags.static import static
from django.utils.html import mark_safe
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin
from unfold.contrib.filters.admin import FieldTextFilter
from unfold.decorators import display
from unfold.sections import TableSection, TemplateSection

from solana.models import Token, TokenPrice

from ..shared.base_admin_model import BaseAdminModel
from ..shared.misc import LargeTablePaginator
from .inlines import WalletTokenStatisticInline


@admin.register(Token)
class TokenAdmin(BaseAdminModel):
    inlines = [WalletTokenStatisticInline]

    readonly_fields = ("created_at", "updated_at")
    list_display = ("logo_display", "symbol", "address", "created_at")
    list_display_links = (
        "logo_display",
        "symbol",
        "address",
    )
    search_fields = ("address", "symbol")
    list_filter = [
        ("address", FieldTextFilter),
        ("name", FieldTextFilter),
    ]

    @display(description=_("Лого"))
    def logo_display(self, obj):
        default_logo_url = static("img/logo.png")
        logo_url = obj.logo if obj.logo else default_logo_url
        return mark_safe(
            f"""<img src="{logo_url}" onerror="this.onerror=null;this.src='{default_logo_url}';" style="width: 40px; height: 40px; border-radius: 50%; object-fit: cover;" />""",
        )


# class CustomTableSection(TableSection):
#     verbose_name = _("Table title")  # Displays custom table title
#     height = 300  # Force the table height. Ideal for large amount of records
#     related_name = "token"  # Related model field name
#     fields = ["id", "address"]  # Fields from related model
#
#
# # class CustomTableSection(TemplateSection):
# #     template_name = r"C:\Python\Мои проекты\CryptoStorage\admin\solana\templates\admin\wallet\test.html"


@admin.register(TokenPrice)
class TokenPriceAdmin(BaseAdminModel):
    autocomplete_fields = ["token"]
    paginator = LargeTablePaginator
    list_display = ["token__symbol", "price_usd", "minute"]
    list_display_links = ["token__symbol", "minute"]
    # list_sections = [
    #     CustomTableSection,
    # ]
