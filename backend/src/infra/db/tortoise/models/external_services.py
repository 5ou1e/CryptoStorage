from tortoise import fields
from tortoise.models import Model

from .common import UUIDIDMixin


class FlipsideConfig(Model, UUIDIDMixin):
    swaps_parsed_until_block_timestamp = fields.DatetimeField(
        null=True,
        blank=True,
        verbose_name="BLOCK_TIMESTAMP до которого собраны транзакции",
    )

    class Meta:
        table = "flipsidecrypto_config"
        verbose_name = "конфиг FlipsideCrypto"
        verbose_name_plural = "конфиг FlipsideCrypto"


class FlipsideAccount(Model, UUIDIDMixin):
    api_key = fields.CharField(max_length=255, verbose_name="API-key")
    is_active = fields.BooleanField(default=True)

    class Meta:
        table = "flipsidecrypto_account"
        verbose_name = "аккаунт FlipsideCrypto"
        verbose_name_plural = "аккаунты FlipsideCrypto"
