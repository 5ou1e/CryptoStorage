from django.core.paginator import Paginator
from django.db import connection
from django.forms import BaseInlineFormSet
from django.utils.functional import cached_property


class LimitModelFormset(BaseInlineFormSet):
    """Base Inline formset to limit inline Model query results."""

    def __init__(self, *args, **kwargs):
        super(LimitModelFormset, self).__init__(*args, **kwargs)
        _kwargs = {self.fk.name: kwargs["instance"]}
        _limit = kwargs.get("limit") or 50
        self.queryset = kwargs["queryset"].filter(**_kwargs).order_by("-pk")[:_limit]


class IntEstimate(int):
    def __str__(self):
        return "{}~".format(int.__str__(self))


class LargeTablePaginator(Paginator):

    @cached_property
    def count(self):
        """Переопределяет базовый метод count, если более 10.000 записей используется функция estimate"""
        limit = 10000
        count = self.object_list.order_by()[:limit].count()
        if count >= limit:
            with connection.cursor() as cursor:
                sql, params = self.object_list.query.sql_with_params()
                query = cursor.mogrify(sql, params)
                cursor.execute("SELECT count_estimate(%s)", [query])
                result = cursor.fetchone()
                count = IntEstimate(result[0])
        return count
