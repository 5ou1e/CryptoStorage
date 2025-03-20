import uuid

import uuid6
from django.db import models


class WalletActivity(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid6.uuid7, editable=False)
    tx_hash = models.CharField(db_index=True, max_length=90, null=True, blank=True, verbose_name="Tx signature")
    timestamp = models.BigIntegerField(db_index=True, null=True, blank=True, verbose_name="Дата транзакции")
    event_type = models.CharField(max_length=15, null=True, blank=True, verbose_name="Тип активности")
    quote_amount = models.DecimalField(max_digits=40, decimal_places=20, null=True, blank=True,
                                       verbose_name="Кол-во SOL")
    token_amount = models.DecimalField(max_digits=40, decimal_places=20, null=True, blank=True,
                                       verbose_name="Кол-во токенов")
    price_usd = models.DecimalField(max_digits=40, decimal_places=20, null=True, blank=True, verbose_name="Цена токена в USD")
    is_part_of_transaction_with_mt_3_swappers = models.BooleanField(default=False, verbose_name="Является ли свап частью транзакции с 3 и более трейдерами")
    is_part_of_arbitrage_swap_event = models.BooleanField(default=False, verbose_name="Является ли свап частью арбитраж свапа")

    wallet = models.ForeignKey('solana.wallet', related_name='activities', on_delete=models.CASCADE,
                               verbose_name='Кошелек')
    token = models.ForeignKey('solana.token', related_name='activities', on_delete=models.CASCADE,
                               verbose_name='Токен')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создана')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлена')

    class Meta:
        db_table = 'swap'
        verbose_name = 'Свап-транзакции'
        verbose_name_plural = 'Свап-транзакции'

    def get_absolute_url(self):
        return "#"
