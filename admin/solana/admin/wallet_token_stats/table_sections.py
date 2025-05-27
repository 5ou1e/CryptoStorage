from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from solana.models import WalletActivity
from unfold.decorators import display
from unfold.sections import TableSection
from utils.number_utils import formatted_number
from utils.time_utils import format_datetime


class SwapsTableSection(TableSection):
    verbose_name = _("Свапы")  # Displays custom table title
    height = 500  # Force the table height. Ideal for large amount of records
    related_name = "swaps_for_table_section"  # Related model field name

    fields = [
        "tx_hash_display",
        "sol_amount_display",
        "token_amount_display",
        "event_type_display",
        "amount_usd_display",
        "timestamp_display",
    ]

    @display(description="TX Signature")
    def tx_hash_display(self, obj: WalletActivity):
        tx_hash = obj.tx_hash

        show_warning = False
        warning_title = ""

        if obj.is_part_of_transaction_with_mt_3_swappers:
            show_warning = True
            warning_title += f"\nБолее 3 трейдеров в транзакции"
        if obj.is_part_of_arbitrage_swap_event:
            show_warning = True
            warning_title += f"\nАрбитраж-свап"

        return mark_safe(
            f"""
                <a href="https://solscan.io/tx/{tx_hash}" target="_blank">{tx_hash}</a>
                {f'<i class="bx bx-error-alt" style="color:#f73d3d "title="{warning_title}"></i>' if show_warning else ''}
            """
        )

    @display(description="Сумма USD")
    def amount_usd_display(self, obj):
        if obj.price_usd is None:
            return None
        value = obj.price_usd * obj.quote_amount
        return formatted_number(value, suffix=" $")

    @display(description="Кол-во токенов")
    def token_amount_display(self, obj):
        if obj.token_amount is None:
            return None
        return formatted_number(obj.token_amount, decimals=2)

    @display(description="Кол-во SOL")
    def sol_amount_display(self, obj):
        if obj.quote_amount is None:
            return None
        return formatted_number(obj.quote_amount)

    @display(description="Дата/Время")
    def timestamp_display(self, obj):
        return format_datetime(obj.timestamp)

    @display(description="Тип")
    def event_type_display(self, obj):
        return obj.event_type
