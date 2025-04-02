from django.utils.translation import gettext_lazy as _
from unfold.sections import TableSection

from ...models import WalletStatistic7d, WalletStatistic30d, WalletStatisticAll


class WalletStats7dTableSection(TableSection):
    verbose_name = _("Статистика за 7 дней")
    height = 300
    related_name = "stats_7d"
    fields = [field.name for field in WalletStatistic7d._meta.fields]


class WalletStats30dTableSection(TableSection):
    verbose_name = _("Статистика за 30 дней")
    height = 300
    related_name = "stats_30d"
    fields = [field.name for field in WalletStatistic30d._meta.fields]


class WalletStatsAllTableSection(TableSection):
    verbose_name = _("Статистика за все время")
    height = 300
    related_name = "stats_all"
    fields = [field.name for field in WalletStatisticAll._meta.fields]
