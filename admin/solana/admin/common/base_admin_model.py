from django.db.models import QuerySet
from django.http import HttpRequest
from unfold.admin import ModelAdmin
from unfold.decorators import action

from solana.admin.common.misc import LargeTablePaginator


class BaseAdminModel(ModelAdmin):
    """Базовая админ-модель"""

    list_per_page = 10
    show_full_result_count = False
    paginator = LargeTablePaginator
    list_filter_submit = True
    list_filter_sheet = True
    list_fullwidth = True
    compressed_fields = True
    search_help_text = "Поиск"
