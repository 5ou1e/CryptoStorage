
import uuid

from asgiref.sync import sync_to_async
from django.db import models, transaction
from django.db.models import F, Q
from django.urls import reverse
from django.utils.timezone import now


class Wallet(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid1, editable=False)
    address = models.CharField(max_length=90, unique=True, verbose_name="Адрес")
    last_stats_check = models.DateTimeField(null=True, blank=True, verbose_name="Статистика обновлена")
    created_at = models.DateTimeField(db_index=True, auto_now_add=True, verbose_name='Создан')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлен')

    class Meta:

        db_table = 'wallet'
        verbose_name = 'кошелек'
        verbose_name_plural = 'кошельки'
        indexes = [
            models.Index(F('last_stats_check').asc(nulls_first=True), name='w_last_stats_check_asc_idx'),
        ]

    def __str__(self):
        return f"{self.address}"

    def get_absolute_url(self):
        return reverse(
            'admin:solana_wallet_changelist'
        ) + f"{self.address}/statistics/"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            from solana.models import (
                WalletDetail,
                WalletPeriodStatistic7d,
                WalletPeriodStatistic30d,
                WalletPeriodStatisticAll,
            )

            # Создаем связанные объекты WalletDetail и WalletStatistic
            WalletDetail.objects.create(wallet=self)
            WalletPeriodStatistic7d.objects.create(wallet=self)
            WalletPeriodStatistic30d.objects.create(wallet=self)
            WalletPeriodStatisticAll.objects.create(wallet=self)

    @classmethod
    def get_wallet_for_update_stats(cls):
        """Синхронный метод для получения кошелька и обновления его статуса."""
        with transaction.atomic():
            wallet = cls.objects.filter(
                Q(stats_check_interval__isnull=False) & # Только кошельки у которых есть интервал чека и
                (Q(last_stats_check__lte=now() - F('stats_check_interval')) | # которые пора чекать по интервалу
                 Q(last_stats_check__isnull=True)) & # или которые не чекались вообще
                Q(stats_check_in_process=False) # Исключаем те, что уже чекаются
            ).order_by(
                # F('last_stats_check').desc(nulls_last=True),
                '-last_stats_check',
                '-created_at',
            ).select_for_update(
                skip_locked=True
            ).last()

            if wallet:
                # Обновляем статус в той же транзакции
                cls.objects.filter(id=wallet.id).update(stats_check_in_process=True)

            return wallet


    @classmethod
    @sync_to_async
    def get_wallet_for_update_stats_async(cls):
        """Асинхронный метод для получения кошелька и обновления его статуса."""
        return cls.get_wallet_for_update_stats()


    @classmethod
    async def bulk_import_wallets(cls, wallets):
        wallets_to_create = []
        _wallets_to_create = {}
        created_wallets = {}

        for wallet in wallets:
            _wallets_to_create[wallet["address"]] = cls(
                address=wallet["address"].replace('\x00', ''),
            )

        # Добавляем все кошельки в список для массового создания
        for key, val in _wallets_to_create.items():
            wallets_to_create.append(val)

        if wallets_to_create:
            # Массовое создание кошельков с игнорированием конфликтов (по уникальному полю address)
            await cls.objects.abulk_create(
                wallets_to_create,
                batch_size=1000,
                ignore_conflicts=True
            )

        # Загружаем созданные кошельки из базы данных по адресам
        created_addresses = [wallet.address for wallet in wallets_to_create]
        time1 = now()

        if created_addresses:
            async for wallet in cls.objects.filter(address__in=created_addresses):
                created_wallets[wallet.address] = wallet

        return created_wallets


class TgSentWallet(models.Model):
    wallet = models.OneToOneField('Wallet', related_name='tg_sent', on_delete=models.CASCADE)
    created_at = models.DateTimeField(db_index=True, auto_now_add=True, verbose_name='Создан')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлен')

    class Meta:
        db_table = 'tg_sent_wallet'


class WalletBuyPriceGt15k(Wallet):
    def get_absolute_url(self):
        return reverse(
            'admin:solana_walletbuypricegt15k_changelist'
        ) + f"{self.address}/statistics/"

    class Meta:
        proxy = True
        verbose_name = "кошелек (Buy price gt 15k)"
        verbose_name_plural = "кошельки (Buy price gt 15k)"


class WalletProxy(Wallet):
    class Meta:
        proxy = True
        verbose_name = "кошелек (базовая)"
        verbose_name_plural = "кошельки (базовая)"