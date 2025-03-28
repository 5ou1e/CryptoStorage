import uuid6
from django.db import models


class WalletTokenStatistic(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid6.uuid7(), editable=False)
    total_buys_count = models.IntegerField(
        null=True, blank=True, verbose_name="Всего покупок"
    )
    total_buy_amount_usd = models.DecimalField(
        null=True,
        blank=True,
        max_digits=40,
        decimal_places=20,
        verbose_name="Общая сумма покупок USD",
    )
    total_buy_amount_token = models.DecimalField(
        null=True,
        blank=True,
        max_digits=40,
        decimal_places=20,
        verbose_name="Общая сумма покупок token-amount",
    )
    first_buy_price_usd = models.DecimalField(
        null=True,
        blank=True,
        max_digits=40,
        decimal_places=20,
        verbose_name="Цена токена в момент 1-й покупки",
    )
    first_buy_timestamp = models.BigIntegerField(
        null=True, blank=True, verbose_name="Время 1-й покупки"
    )

    total_sales_count = models.IntegerField(
        null=True, blank=True, verbose_name="Всего продаж"
    )
    total_sell_amount_usd = models.DecimalField(
        null=True,
        blank=True,
        max_digits=40,
        decimal_places=20,
        verbose_name="Общая сумма продаж USD",
    )
    total_sell_amount_token = models.DecimalField(
        null=True,
        blank=True,
        max_digits=40,
        decimal_places=20,
        verbose_name="Общая сумма продаж token-amount",
    )
    first_sell_price_usd = models.DecimalField(
        null=True,
        blank=True,
        max_digits=40,
        decimal_places=20,
        verbose_name="Цена токена в момент 1-й продажи",
    )
    first_sell_timestamp = models.BigIntegerField(
        null=True, blank=True, verbose_name="Время 1-й продажи"
    )

    last_activity_timestamp = models.BigIntegerField(
        null=True, blank=True, verbose_name="Последняя активность"
    )

    total_profit_usd = models.DecimalField(
        null=True,
        blank=True,
        max_digits=40,
        decimal_places=20,
        verbose_name="Общий профит в USD",
    )
    total_profit_percent = models.FloatField(
        null=True, blank=True, verbose_name="Общий профит %"
    )
    first_buy_sell_duration = models.IntegerField(
        null=True, blank=True, verbose_name="Холд между 1-й покупкой и продажей"
    )
    total_swaps_from_txs_with_mt_3_swappers = models.IntegerField(
        default=0,
        verbose_name="Кол-во активностей являющихся частью транзакций с более чем 3 трейдерами",
    )
    total_swaps_from_arbitrage_swap_events = models.IntegerField(
        default=0,
        verbose_name="Кол-во активностей являющихся частью арбитражных свап-эвентов",
    )

    wallet = models.ForeignKey(
        "solana.wallet",
        related_name="wallet_token_statistic",
        on_delete=models.CASCADE,
        verbose_name="Кошелек",
    )
    token = models.ForeignKey(
        "solana.token",
        related_name="wallet_token_statistic",
        on_delete=models.CASCADE,
        verbose_name="Токен",
        db_index=True,
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создана")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлена")

    class Meta:
        db_table = "wallet_token"
        verbose_name = "кошелек-токен"
        verbose_name_plural = "кошелек-токены"
        constraints = [
            models.UniqueConstraint(
                fields=["wallet", "token"], name="unique_wallet_token"
            )
        ]

    def __str__(self):
        return f"Токен - {self.token.address}, Кошелек - {self.wallet.address}"
