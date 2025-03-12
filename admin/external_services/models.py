from django.db import models


class FlipsideCryptoConfig(models.Model):
    swaps_parsed_untill_inserted_timestamp = models.DateTimeField(null=True, blank=True, verbose_name="INSERTED_TIMESTAMP до которого собраны транзакции")

    class Meta:
        db_table = 'flipsidecrypto_config'
        verbose_name = 'конфиг FlipsideCrypto'
        verbose_name_plural = 'конфиг FlipsideCrypto'

    def __str__(self):
        return str(self.id)


class FlipsideCryptoAccount(models.Model):
    api_key = models.CharField(max_length=255, verbose_name='API-key')
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'flipsidecrypto_account'
        verbose_name = 'аккаунт FlipsideCrypto'
        verbose_name_plural = 'аккаунты FlipsideCrypto'

    def __str__(self):
        return str(self.id)