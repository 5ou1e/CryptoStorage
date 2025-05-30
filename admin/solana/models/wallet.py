import uuid

import uuid6
from asgiref.sync import sync_to_async
from django.db import models, transaction
from django.db.models import F, Q
from django.urls import reverse
from django.utils.timezone import now


class WalletBase(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid6.uuid7, editable=False)
    address = models.CharField(max_length=90, unique=True, verbose_name="Адрес")
    last_stats_check = models.DateTimeField(
        null=True, blank=True, verbose_name="Статистика обновлена"
    )
    is_scammer = models.BooleanField(null=False, default=False)
    is_bot = models.BooleanField(null=False, default=False)
    sol_balance = models.DecimalField(max_digits=40, decimal_places=20, null=True)
    created_at = models.DateTimeField(
        db_index=True, auto_now_add=True, verbose_name="Создан"
    )
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлен")

    class Meta:

        db_table = "wallet"
        verbose_name = "кошелек (базовая)"
        verbose_name_plural = "кошельки (базовая)"
        indexes = [
            models.Index(
                F("last_stats_check").asc(nulls_first=True),
                name="w_last_stats_check_asc_idx",
            ),
        ]

    def __str__(self):
        return f"{self.address}"

    def get_stats_url(self):
        return reverse("admin:solana_wallet_changelist") + f"{self.address}/"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            from solana.models import (WalletStatistic7d, WalletStatistic30d,
                                       WalletStatisticAll)

            WalletStatistic7d.objects.create(wallet=self)
            WalletStatistic30d.objects.create(wallet=self)
            WalletStatisticAll.objects.create(wallet=self)


class TgSentWallet(models.Model):
    wallet = models.OneToOneField(
        "WalletBase", related_name="tg_sent", on_delete=models.CASCADE, primary_key=True
    )
    created_at = models.DateTimeField(
        db_index=True, auto_now_add=True, verbose_name="Создан"
    )
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлен")

    class Meta:
        db_table = "tg_sent_wallet"


class Wallet(WalletBase):
    """Прокси-модель основной таблицы кошельков"""

    class Meta:
        proxy = True
        verbose_name = "кошелек"
        verbose_name_plural = "кошельки"


class WalletFilteredBase(models.Model):
    wallet = models.OneToOneField(
        "WalletBase",
        related_name="wallet_filtered",
        on_delete=models.CASCADE,
        primary_key=True,
    )

    class Meta:
        db_table = "wallet_filtered"


class WalletBuyPriceGt15k(WalletBase):
    """Прокси-модель таблицы кошельков со статой по токенам с покупкой от 15к+"""

    def get_stats_url(self):
        return (
            reverse("admin:solana_walletbuypricegt15k_changelist") + f"{self.address}/"
        )

    class Meta:
        proxy = True
        verbose_name = "кошелек (Buy price gt 15k)"
        verbose_name_plural = "кошельки (Buy price gt 15k)"


class WalletCopyableBase(models.Model):
    wallet = models.OneToOneField(
        "WalletBase",
        related_name="wallet_copyable",
        on_delete=models.CASCADE,
        primary_key=True,
    )

    class Meta:
        db_table = "wallet_copyable"


class WalletCopyable(WalletBase):
    """Прокси-модель таблицы копируемых кошельков"""

    def get_stats_url(self):
        return reverse("admin:solana_walletcopyable_changelist") + f"{self.address}/"

    class Meta:
        proxy = True
        verbose_name = "кошелек (Копируемые)"
        verbose_name_plural = "кошельки (Копируемые)"
