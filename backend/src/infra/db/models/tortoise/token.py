from tortoise import Model, fields

from .common import IntIDMixin, TimestampsMixin, UUIDIDMixin


class Token(Model, UUIDIDMixin, TimestampsMixin):
    address = fields.CharField(max_length=90, unique=True)
    name = fields.CharField(max_length=100, null=True, blank=True)
    symbol = fields.CharField(max_length=100, null=True, blank=True)
    uri = fields.TextField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name="Token Metaplex Metadata Uri",
    )
    logo = fields.TextField(max_length=255, null=True, blank=True)
    created_on = fields.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="Создан на",
    )
    is_metadata_parsed = fields.BooleanField(default=False)

    class Meta:
        table = "token"

    def __str__(self):
        return self.address


class TokenPrice(Model, UUIDIDMixin, TimestampsMixin):
    token = fields.ForeignKeyField(
        "models.Token",
        related_name="token_price",
        on_delete=fields.CASCADE,
        verbose_name="Токен",
    )
    price_usd = fields.DecimalField(
        max_digits=40,
        decimal_places=20,
        null=True,
        blank=True,
        verbose_name="Цена в USD",
    )
    minute = fields.DatetimeField(verbose_name="Минута свечи")

    class Meta:
        table = "token_price"
        indexes = [
            ("token",),
        ]
        unique_together = ("token", "minute")

    def __str__(self):
        return f"Цена {self.token.symbol} в {self.minute}"
