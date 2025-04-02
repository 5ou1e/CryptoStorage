from typing import Optional

from tortoise import Model, fields
from tortoise.fields.relational import BackwardOneToOneRelation

from .common import CorrectedDecimalField, TimestampsMixin, UUIDIDMixin


class Wallet(Model, UUIDIDMixin, TimestampsMixin):
    address = fields.CharField(max_length=90, unique=True)
    last_stats_check = fields.DatetimeField(null=True, blank=True)
    sol_balance = CorrectedDecimalField(
        max_digits=50,
        decimal_places=20,
        null=True,
        blank=True,
    )
    is_scammer = fields.BooleanField(
        db_index=True,
        default=False,
        verbose_name="Скамерский кошелек",
    )
    is_bot = fields.BooleanField(
        db_index=True,
        default=False,
        verbose_name="Арбитраж-бот",
    )
    stats_7d: BackwardOneToOneRelation["WalletStatistic7d"]
    stats_30d: BackwardOneToOneRelation["WalletStatistic30d"]
    stats_all: BackwardOneToOneRelation["WalletStatisticAll"]
    last_activity_timestamp = fields.DatetimeField(
        null=True,
        description="Время последней Defi-активности",
    )
    first_activity_timestamp = fields.DatetimeField(null=True, description="Время первой Defi-активности")

    class Meta:
        table = "wallet"
        indexes = [
            ("created_at",),  # Также в идеале нужен индекс на DESC
            # ('last_stats_check',),  # нужен индекс NULLS FIRST
            # ('last_activity_timestamp', 'last_stats_check'),  # для апдейта статистики last_stats_check NULLS FIRST
            # ('last_stats_check', 'last_activity_timestamp'),  # для апдейта статистики last_stats_check NULLS FIRST
            ("is_bot",),
            ("is_scammer",),
            ("last_activity_timestamp",),
            ("address",),
        ]

    def __str__(self):
        return f"{self.address}"


class AbstractWalletStatistic(Model, TimestampsMixin):
    wallet = fields.OneToOneField(
        "models.Wallet",
        related_name="wallet_statistic_period_abstract",
        on_delete=fields.CASCADE,
        pk=True,
    )
    winrate = CorrectedDecimalField(
        max_digits=40,
        decimal_places=5,
        null=True,
        blank=True,
        index=True,
    )
    total_token_buy_amount_usd = CorrectedDecimalField(
        max_digits=50,
        decimal_places=20,
        null=True,
        blank=True,
    )
    total_token_sell_amount_usd = CorrectedDecimalField(
        max_digits=50,
        decimal_places=20,
        null=True,
        blank=True,
    )
    total_profit_usd = CorrectedDecimalField(
        max_digits=50,
        decimal_places=20,
        null=True,
        blank=True,
        index=True,
    )
    total_profit_multiplier = fields.FloatField(null=True, blank=True, index=True)
    total_token = fields.IntField(null=True, blank=True, index=True)
    total_token_buys = fields.IntField(null=True, blank=True)
    total_token_sales = fields.IntField(null=True, blank=True)
    token_with_buy_and_sell = fields.IntField(null=True, blank=True)
    token_with_buy = fields.IntField(null=True, blank=True)
    token_sell_without_buy = fields.IntField(null=True, blank=True)
    token_buy_without_sell = fields.IntField(null=True, blank=True)
    token_with_sell_amount_gt_buy_amount = fields.IntField(null=True, blank=True)
    token_avg_buy_amount = CorrectedDecimalField(
        max_digits=50,
        decimal_places=20,
        null=True,
        blank=True,
        index=True,
    )
    token_median_buy_amount = CorrectedDecimalField(
        max_digits=50,
        decimal_places=20,
        null=True,
        blank=True,
    )
    token_first_buy_avg_price_usd = CorrectedDecimalField(
        max_digits=50,
        decimal_places=20,
        null=True,
        blank=True,
    )
    token_first_buy_median_price_usd = CorrectedDecimalField(
        max_digits=50,
        decimal_places=20,
        null=True,
        blank=True,
        index=True,
    )
    token_avg_profit_usd = CorrectedDecimalField(
        max_digits=50,
        decimal_places=20,
        null=True,
        blank=True,
        index=True,
    )
    token_buy_sell_duration_avg = fields.BigIntField(null=True, blank=True)
    token_buy_sell_duration_median = fields.BigIntField(null=True, blank=True, index=True)
    pnl_lt_minus_dot5_num = fields.IntField(null=True, blank=True)
    pnl_minus_dot5_0x_num = fields.IntField(null=True, blank=True)
    pnl_lt_2x_num = fields.IntField(null=True, blank=True)
    pnl_2x_5x_num = fields.IntField(null=True, blank=True)
    pnl_gt_5x_num = fields.IntField(null=True, blank=True)
    pnl_lt_minus_dot5_percent = fields.FloatField(null=True, blank=True)
    pnl_minus_dot5_0x_percent = fields.FloatField(null=True, blank=True)
    pnl_lt_2x_percent = fields.FloatField(null=True, blank=True)
    pnl_2x_5x_percent = fields.FloatField(null=True, blank=True)
    pnl_gt_5x_percent = fields.FloatField(null=True, blank=True)

    @property
    def total_buys_and_sales_count(self) -> int:
        return (
            self.total_token_buys + self.total_token_sales if (self.total_token_buys and self.total_token_sales) else 0
        )

    total_swaps_from_arbitrage_swap_events: Optional[int] = 0
    total_swaps_from_txs_with_mt_3_swappers: Optional[int] = 0

    class Meta:
        abstract = True


class WalletStatistic7d(AbstractWalletStatistic):
    wallet = fields.OneToOneField("models.Wallet", related_name="stats_7d", on_delete=fields.CASCADE, pk=True)

    class Meta:
        table = "wallet_statistic_7d"

    def __str__(self):
        return "Статистика кошелька за 7д"


class WalletStatistic30d(AbstractWalletStatistic):
    wallet = fields.OneToOneField("models.Wallet", related_name="stats_30d", on_delete=fields.CASCADE, pk=True)

    class Meta:
        table = "wallet_statistic_30d"

    def __str__(self):
        return "Статистика кошелька за 30д"


class WalletStatisticAll(AbstractWalletStatistic):
    wallet = fields.OneToOneField("models.Wallet", related_name="stats_all", on_delete=fields.CASCADE, pk=True)

    class Meta:
        table = "wallet_statistic_all"

    def __str__(self):
        return "Статистика кошелька за все время"


class WalletStatisticBuyPriceGt15k7d(AbstractWalletStatistic):
    wallet = fields.OneToOneField(
        "models.Wallet",
        related_name="stats_buy_price_gt_15k_7d",
        on_delete=fields.CASCADE,
        pk=True,
    )

    class Meta:
        table = "wallet_statistic_buy_price_gt_15k_7d"

    def __str__(self):
        return "Статистика кошелька за 7д"


class WalletStatisticBuyPriceGt15k30d(AbstractWalletStatistic):
    wallet = fields.OneToOneField(
        "models.Wallet",
        related_name="stats_buy_price_gt_15k_30d",
        on_delete=fields.CASCADE,
        pk=True,
    )

    class Meta:
        table = "wallet_statistic_buy_price_gt_15k_30d"

    def __str__(self):
        return "Статистика кошелька за 30д"


class WalletStatisticBuyPriceGt15kAll(AbstractWalletStatistic):
    wallet = fields.OneToOneField(
        "models.Wallet",
        related_name="stats_buy_price_gt_15k_all",
        on_delete=fields.CASCADE,
        pk=True,
    )

    class Meta:
        table = "wallet_statistic_buy_price_gt_15k_all"

    def __str__(self):
        return "Статистика кошелька за все время"


class WalletToken(Model, UUIDIDMixin, TimestampsMixin):

    total_buys_count = fields.IntField(default=0, description="Всего покупок")
    total_buy_amount_usd = CorrectedDecimalField(
        max_digits=40,
        decimal_places=20,
        default=0,
        description="Общая сумма покупок USD",
    )
    total_buy_amount_token = CorrectedDecimalField(
        max_digits=40,
        decimal_places=20,
        default=0,
        description="Общая сумма покупок token-amount",
    )
    first_buy_price_usd = CorrectedDecimalField(
        max_digits=40,
        decimal_places=20,
        null=True,
        description="Цена токена в момент 1-й покупки",
    )
    first_buy_timestamp = fields.DatetimeField(null=True, description="Время 1-й покупки")
    total_sales_count = fields.IntField(default=0, description="Всего продаж")
    total_sell_amount_usd = CorrectedDecimalField(
        max_digits=40,
        decimal_places=20,
        default=0,
        description="Общая сумма продаж USD",
    )
    total_sell_amount_token = CorrectedDecimalField(
        max_digits=40,
        decimal_places=20,
        default=0,
        description="Общая сумма продаж token-amount",
    )
    first_sell_price_usd = CorrectedDecimalField(
        max_digits=40,
        decimal_places=20,
        null=True,
        description="Цена токена в момент 1-й продажи",
    )
    first_sell_timestamp = fields.DatetimeField(null=True, description="Время 1-й продажи")
    last_activity_timestamp = fields.DatetimeField(null=True, description="Последняя активность")
    total_profit_usd = CorrectedDecimalField(
        default=0,
        max_digits=40,
        decimal_places=20,
        description="Общий профит в USD",
    )
    total_profit_percent = fields.FloatField(null=True, description="Общий профит %")
    first_buy_sell_duration = fields.IntField(
        null=True,
        description="Холд между 1-й покупкой и продажей",
    )
    total_swaps_from_txs_with_mt_3_swappers = fields.IntField(
        default=0,
        description="Кол-во свапов являющихся частью транзакций с >= 3 трейдерами",
    )
    total_swaps_from_arbitrage_swap_events = fields.IntField(
        default=0,
        description="Кол-во свапов являющихся частью арбитражных транз.",
    )

    wallet = fields.ForeignKeyField(
        "models.Wallet",
        related_name="tokens",
        on_delete=fields.CASCADE,
        description="Кошелек",
    )
    token = fields.ForeignKeyField(
        "models.Token",
        related_name="wallets",
        on_delete=fields.CASCADE,
        description="Токен",
    )

    class Meta:
        table = "wallet_token"
        verbose_name = "кошелек-токен"
        verbose_name_plural = "кошелек-токен"
        unique_together = ("wallet", "token")
        indexes = [
            ("wallet",),
            ("token",),
        ]


class TgSentWallet(Model, TimestampsMixin):
    wallet = fields.OneToOneField("models.Wallet", related_name="tg_sent", on_delete=fields.CASCADE, pk=True)

    class Meta:
        table = "tg_sent_wallet"
