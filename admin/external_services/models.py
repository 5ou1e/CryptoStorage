from django.db import models
from uuid6 import uuid7


class FlipsideConfig(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid7, editable=False)
    swaps_parsed_until_block_timestamp = models.DateTimeField(null=True, blank=True, verbose_name="BLOCK_TIMESTAMP до которого собраны транзакции")

    class Meta:
        db_table = 'flipsidecrypto_config'
        verbose_name = 'конфиг FlipsideCrypto'
        verbose_name_plural = 'конфиг FlipsideCrypto'

    def __str__(self):
        return str(self.id)


class FlipsideAccount(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid7, editable=False)
    api_key = models.CharField(max_length=255, verbose_name='API-key')
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'flipsidecrypto_account'
        verbose_name = 'аккаунт FlipsideCrypto'
        verbose_name_plural = 'аккаунты FlipsideCrypto'

    def __str__(self):
        return str(self.id)
