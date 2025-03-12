from django.db import models


class WalletDetail(models.Model):
    wallet = models.OneToOneField('solana.wallet', related_name='details', on_delete=models.CASCADE,
                               verbose_name='Кошелек')
    sol_balance = models.DecimalField(max_digits=50, decimal_places=20, null=True, blank=True, verbose_name='SOL Balance')
    is_scammer = models.BooleanField(db_index=True, default=False, null=True, verbose_name='Скамер')
    is_bot = models.BooleanField(db_index=True, default=False, null=True, verbose_name='Бот')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создана')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлена')

    class Meta:
        db_table = 'wallet_detail'
        verbose_name = 'детали кошелька'
        verbose_name_plural = 'детали кошельков'

    def __str__(self):
        return f"Детали кошелька {self.wallet.address}"

