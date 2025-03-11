from tortoise import fields
from tortoise.models import Model

from .common import IntIDMixin


class FlipsideCryptoConfig(Model, IntIDMixin):
    # TODO: swaps_parsed_untill_inserted_timestamp - сейчас это BLOCK_TIMESTAMP
    swaps_parsed_untill_inserted_timestamp = fields.DatetimeField(
        null=True,
        blank=True,
        verbose_name="INSERTED_TIMESTAMP до которого собраны транзакции",
    )

    class Meta:
        table = "flipsidecrypto_config"
        verbose_name = "конфиг FlipsideCrypto"
        verbose_name_plural = "конфиг FlipsideCrypto"


class FlipsideCryptoAccount(Model, IntIDMixin):
    api_key = fields.CharField(max_length=255, verbose_name="API-key")
    is_active = fields.BooleanField(default=True)

    class Meta:
        table = "flipsidecrypto_account"
        verbose_name = "аккаунт FlipsideCrypto"
        verbose_name_plural = "аккаунты FlipsideCrypto"
