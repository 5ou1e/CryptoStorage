from tortoise import Model, fields

from .common import TimestampsMixin, UUIDIDMixin
from .utils import MyDecimalField


class Swap(Model, UUIDIDMixin, TimestampsMixin):
    wallet = fields.ForeignKeyField(
        "models.Wallet",
        related_name="swaps",
        on_delete=fields.CASCADE,
    )
    token = fields.ForeignKeyField(
        "models.Token",
        related_name="swaps",
        on_delete=fields.CASCADE,
    )
    tx_hash = fields.CharField(max_length=90, null=True, blank=True)
    block_id = fields.BigIntField(null=True)
    timestamp = fields.BigIntField(null=True, blank=True)
    event_type = fields.CharField(max_length=15, null=True, blank=True)
    quote_amount = MyDecimalField(
        max_digits=40,
        decimal_places=20,
        null=True,
        blank=True,
    )
    token_amount = MyDecimalField(
        max_digits=40,
        decimal_places=20,
        null=True,
        blank=True,
    )
    cost_usd = MyDecimalField(
        max_digits=40,
        decimal_places=20,
        null=True,
        blank=True,
    )
    price_usd = MyDecimalField(
        max_digits=40,
        decimal_places=20,
        null=True,
        blank=True,
    )
    is_part_of_transaction_with_mt_3_swappers = fields.BooleanField(
        default=False,
        verbose_name="Является ли свап частью транзакции с 3+ трейдерами",
    )
    is_part_of_arbitrage_swap_event = fields.BooleanField(
        default=False,
        verbose_name="Является ли свап частью арбитраж свапа",
    )

    class Meta:
        table = "swap"
        indexes = [
            ("tx_hash",),
            ("block_id",),
            ("timestamp",),
        ]
