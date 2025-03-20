from django.db import models


class AbstractWalletPeriodStatistic(models.Model):
    wallet = models.OneToOneField('solana.wallet', related_name='wallet_statistic_period_abstract', on_delete=models.CASCADE,
                               verbose_name='Кошелек', primary_key=True)
    winrate = models.DecimalField(db_index=True, max_digits=40, decimal_places=5, null=True, blank=True, verbose_name='Winrate') # Только для токенов у которых была покупка!
    total_token_buy_amount_usd = models.DecimalField(max_digits=50, decimal_places=20, null=True, blank=True, verbose_name='Total_tokens_buy_amount_usd')
    total_token_sell_amount_usd = models.DecimalField(max_digits=50, decimal_places=20, null=True, blank=True,
                                                          verbose_name='Total_tokens_sell_amount_usd')
    total_profit_usd = models.DecimalField(db_index=True, max_digits=50, decimal_places=20, null=True, blank=True, verbose_name='Total Profit')# Только для токенов у которых была покупка!
    total_profit_multiplier = models.FloatField(db_index=True, null=True, blank=True, verbose_name="Общий профит %")
    total_token = models.IntegerField(db_index=True, null=True, blank=True, verbose_name='Total tokens')
    total_token_buys = models.IntegerField(null=True, blank=True, verbose_name='Total tokens bought')
    total_token_sales = models.IntegerField(null=True, blank=True, verbose_name='Total tokens sales')
    token_with_buy_and_sell = models.IntegerField(null=True, blank=True, verbose_name='Токенов с покупкой и продажей')
    token_with_buy = models.IntegerField(null=True, blank=True, verbose_name='Токенов с покупкой')
    token_sell_without_buy = models.IntegerField(null=True, blank=True, verbose_name='Токенов с продажей без покупок')
    token_buy_without_sell = models.IntegerField(null=True, blank=True, verbose_name='Токенов с покупкой без продаж')
    token_with_sell_amount_gt_buy_amount = models.IntegerField(null=True, blank=True, verbose_name='Токенов с суммой продаж больше суммы покупок', help_text="По кол-ву единиц токена,  только для токенов у которых есть и продажи и покупки ")
    token_avg_buy_amount = models.DecimalField(db_index=True, max_digits=50, decimal_places=20, null=True, blank=True, verbose_name='Средняя общая сумма покупки токена')
    token_median_buy_amount = models.DecimalField(max_digits=50, decimal_places=20, null=True, blank=True,
                                                   verbose_name='Медиана общей суммы покупки токена')
    token_first_buy_avg_price_usd = models.DecimalField(max_digits=50, decimal_places=20, null=True, blank=True, verbose_name='Средняя стоимость токена в момент первой покупки')
    token_first_buy_median_price_usd = models.DecimalField(db_index=True, max_digits=50, decimal_places=20, null=True, blank=True, verbose_name='Средняя стоимость токена в момент первой покупки')
    token_avg_profit_usd = models.DecimalField(db_index=True, max_digits=50, decimal_places=20, null=True, blank=True, verbose_name='Token avg profit') # Только для токенов у которых была покупка!
    token_buy_sell_duration_avg = models.BigIntegerField(null=True, blank=True, verbose_name='Duration Avg')
    token_buy_sell_duration_median = models.BigIntegerField(db_index=True, null=True, blank=True, verbose_name='Duration Median')
    pnl_lt_minus_dot5_num = models.IntegerField(null=True, blank=True, verbose_name='PnL < -0.5 Number')
    pnl_minus_dot5_0x_num = models.IntegerField(null=True, blank=True, verbose_name='PnL between -0.5 and 0x Number')
    pnl_lt_2x_num = models.IntegerField(null=True, blank=True, verbose_name='PnL < 2x Number All')
    pnl_2x_5x_num = models.IntegerField(null=True, blank=True, verbose_name='PnL between 2x and 5x Number')
    pnl_gt_5x_num = models.IntegerField(null=True, blank=True, verbose_name='PnL > 5x Number')
    pnl_lt_minus_dot5_percent = models.FloatField(null=True, blank=True, verbose_name='PnL < -0.5 Percent')
    pnl_minus_dot5_0x_percent = models.FloatField(null=True, blank=True, verbose_name='PnL between -0.5 and 0x Percent')
    pnl_lt_2x_percent = models.FloatField(null=True, blank=True, verbose_name='PnL < 2x Percent')
    pnl_2x_5x_percent = models.FloatField(null=True, blank=True, verbose_name='PnL between 2x and 5x Percent')
    pnl_gt_5x_percent = models.FloatField(null=True, blank=True, verbose_name='PnL > 5x Percent')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создана')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлена')

    class Meta:
        abstract = True


class WalletPeriodStatistic7d(AbstractWalletPeriodStatistic):
    wallet = models.OneToOneField('solana.wallet', related_name='stats_7d', on_delete=models.CASCADE,
                               verbose_name='Кошелек', primary_key=True)

    class Meta:
        db_table = "wallet_statistic_7d"
        verbose_name = "статистика кошелька за 7 дн"
        verbose_name_plural = "статистики кошельков за 7 дн"
        indexes = [
            models.Index(fields=['wallet'])
        ]

    def __str__(self):
        return "Статистика кошелька за 7д"


class WalletPeriodStatistic30d(AbstractWalletPeriodStatistic):
    wallet = models.OneToOneField('solana.wallet', related_name='stats_30d', on_delete=models.CASCADE,
                               verbose_name='Кошелек', primary_key=True)

    class Meta:
        db_table = "wallet_statistic_30d"
        verbose_name = "статистика кошелька за 30 дн"
        verbose_name_plural = "статистики кошельков за 30 дн"
        indexes = [
            models.Index(fields=['wallet'])
        ]


    def __str__(self):
        return "Статистика кошелька за 30д"


class WalletPeriodStatisticAll(AbstractWalletPeriodStatistic):

    wallet = models.OneToOneField('solana.wallet', related_name='stats_all', on_delete=models.CASCADE,
                               verbose_name='Кошелек', primary_key=True)

    class Meta:
        db_table = "wallet_statistic_all"
        verbose_name = "статистика кошелька за все 90 время"
        verbose_name_plural = "статистики кошельков за все 90 время"
        indexes = [
            models.Index(fields=['wallet'])
        ]

    def __str__(self):
        return "Статистика кошелька за все время"


class WalletPeriodStatisticBuyPriceGt15k7d(AbstractWalletPeriodStatistic):
    wallet = models.OneToOneField('solana.wallet', related_name='stats_buy_price_gt_15k_7d', on_delete=models.CASCADE,
                               verbose_name='Кошелек', primary_key=True)

    class Meta:
        db_table = "wallet_statistic_buy_price_gt_15k_7d"
        verbose_name = "статистика кошелька за 7 дн"
        verbose_name_plural = "статистики кошельков за 7 дн"
        indexes = [
            models.Index(fields=['wallet'])
        ]

    def __str__(self):
        return "Статистика кошелька за 7д"


class WalletPeriodStatisticBuyPriceGt15k30d(AbstractWalletPeriodStatistic):
    wallet = models.OneToOneField('solana.wallet', related_name='stats_buy_price_gt_15k_30d', on_delete=models.CASCADE,
                               verbose_name='Кошелек', primary_key=True)

    class Meta:
        db_table = "wallet_statistic_buy_price_gt_15k_30d"
        verbose_name = "статистика кошелька за 30 дн"
        verbose_name_plural = "статистики кошельков за 30 дн"
        indexes = [
            models.Index(fields=['wallet'])
        ]

    def __str__(self):
        return "Статистика кошелька за 30д"


class WalletPeriodStatisticBuyPriceGt15kAll(AbstractWalletPeriodStatistic):
    wallet = models.OneToOneField('solana.wallet', related_name='stats_buy_price_gt_15k_all', on_delete=models.CASCADE,
                               verbose_name='Кошелек', primary_key=True)

    class Meta:
        db_table = "wallet_statistic_buy_price_gt_15k_all"
        verbose_name = "статистика кошелька за все время"
        verbose_name_plural = "статистики кошельков за все время"
        indexes = [
            models.Index(fields=['wallet'])
        ]

    def __str__(self):
        return "Статистика кошелька за все время"
