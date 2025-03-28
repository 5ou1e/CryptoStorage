from unfold.admin import ModelAdmin

from solana.admin.shared.misc import LargeTablePaginator


class BaseAdminModel(ModelAdmin):
    """Базовая админ-модель"""

    list_per_page = 20
    show_full_result_count = False
    paginator = LargeTablePaginator
    list_filter_submit = True
    list_filter_sheet = True
    list_fullwidth = True
    compressed_fields = True
    search_help_text = "Поиск"
