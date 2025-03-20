import json
from uuid6 import uuid7

from django.db import models
from django.utils.timezone import now


class PrettyJSONEncoder(json.JSONEncoder):
    def __init__(self, *args, indent, sort_keys, **kwargs):
        super().__init__(*args, indent=4, sort_keys=True, **kwargs)


class Token(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid7(), editable=False)
    address = models.CharField(max_length=255, unique=True, verbose_name='Адрес')
    name = models.CharField(max_length=255, null=True, blank=True, verbose_name='Название')
    symbol = models.CharField(max_length=255, null=True, blank=True, verbose_name='Символ')
    uri = models.URLField(max_length=200, null=True, blank=True, verbose_name='Token Metaplex Metadata Uri')
    logo = models.URLField(max_length=255, null=True, blank=True, verbose_name='Logo')
    created_on = models.CharField(max_length=255, null=True, blank=True, verbose_name='Создан на')
    is_metadata_parsed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Добавлен')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлен')

    class Meta:
        db_table = 'token'
        verbose_name = 'токен'
        verbose_name_plural = 'токены'

    @classmethod
    async def bulk_import_tokens(cls, tokens):
        tokens_to_create = []
        _tokens_to_create = {}
        created_tokens = {}

        for token in tokens:
            _tokens_to_create[token["address"]] = cls(
                address=token["address"].replace('\x00', ''),
                name=token['symbol'].replace('\x00', '') if token.get('symbol') else None,
                decimals=token['decimals'] if token.get('decimals') else None,
                logo=token['logo'][:500].replace('\x00', '') if token.get('logo') else None,
                price=token['price'] if token.get('price') else None,
                symbol=token['symbol'].replace('\x00', '') if token.get('symbol') else None,
            )

        # Добавляем все токены в список для массового создания
        for key, val in _tokens_to_create.items():
            tokens_to_create.append(val)

        if tokens_to_create:
            # Массовое создание токенов с игнорированием конфликтов (по уникальному полю address)
            await cls.objects.abulk_create(
                tokens_to_create,
                batch_size=1000,
                ignore_conflicts=True
            )

        # Загружаем созданные токены из базы данных по адресам
        created_addresses = [token.address for token in tokens_to_create]
        time1 = now()

        if created_addresses:
            async for token in cls.objects.filter(address__in=created_addresses):
                created_tokens[token.address] = token

        return created_tokens


    def __str__(self):
        return f"{self.symbol}"


class TokenPrice(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid7(), editable=False)
    token = models.ForeignKey('solana.token', related_name='token_price', on_delete=models.CASCADE,
                               verbose_name='Токен')
    price_usd = models.DecimalField(max_digits=40, decimal_places=20, null=True, blank=True, verbose_name='Цена в USD')
    minute = models.DateTimeField(verbose_name='Время (по минутам)')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создана')

    class Meta:
        db_table = 'token_price'
        verbose_name = 'цена токена'
        verbose_name_plural = 'цены токенов'
        indexes = [
            models.Index(fields=['token']),
            models.Index(fields=['token', 'minute']),
        ]

        constraints = [
            models.UniqueConstraint(fields=['token', 'minute'], name="unique_tokenprice_token_minute")
        ]
