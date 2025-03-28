from django.contrib import admin
from django.utils.timezone import localtime
from unfold.admin import ModelAdmin
from unfold.decorators import display

from .models import FlipsideAccount, FlipsideConfig


@admin.register(FlipsideConfig)
class FlipsideConfigAdmin(ModelAdmin):
    list_per_page = 30
    list_display = [
        "swaps_parsed_until_block_timestamp_display"
    ]  # + [field.name for field in GmgnWalletActivity._meta.get_fields()]
    list_display_links = ["swaps_parsed_until_block_timestamp_display"]

    @display(
        description=("BLOCK_TIMESTAMP до которого собраны транзакции (MSK)"),
        ordering="-wallet__address",
    )
    # Функция для форматирования времени с миллисекундами
    def swaps_parsed_until_block_timestamp_display(self, obj):
        return localtime(obj.swaps_parsed_until_block_timestamp).strftime(
            "%Y-%m-%d %H:%M:%S.%f"
        )


@admin.register(FlipsideAccount)
class FlipsideAccountAdmin(ModelAdmin):
    list_per_page = 30
    list_display = [
        "api_key",
        "is_active",
    ]  # + [field.name for field in GmgnWalletActivity._meta.get_fields()]
    list_display_links = ["api_key", "is_active"]
