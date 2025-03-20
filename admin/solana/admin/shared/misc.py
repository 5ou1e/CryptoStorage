from django.core.paginator import Paginator
from django.db import connection
from django.forms import BaseInlineFormSet
from django.utils.functional import cached_property


class LimitModelFormset(BaseInlineFormSet):
    """ Base Inline formset to limit inline Model query results. """
    def __init__(self, *args, **kwargs):
        super(LimitModelFormset, self).__init__(*args, **kwargs)
        _kwargs = {self.fk.name: kwargs['instance']}
        _limit = kwargs.get('limit') or 50
        self.queryset = kwargs['queryset'].filter(**_kwargs).order_by('-pk')[:_limit]


class IntEstimate(int):
    def __str__(self):
        return '{}+'.format(int.__str__(self))


class LargeTablePaginator(Paginator):

    @cached_property
    def count(self):
        """Changed to use an estimate if the estimate is greater than 10,000
        Returns the total number of objects, across all pages."""
        try:
            estimate = 0
            if not self.object_list.query.where:
                try:
                    cursor = connection.cursor()
                    cursor.execute(
                        'SELECT reltuples FROM pg_class WHERE relname = %s',
                        [self.object_list.query.model._meta.db_table])
                    estimate = int(cursor.fetchone()[0])
                except:
                    pass
            if estimate < 1000:
                limit = 50000
                self._count = self.object_list.order_by()[:limit].count()
                if not self._count < limit:
                    return IntEstimate(self._count)
                if not self._count < limit:
                    query = str(self.object_list.query)  # Получаем SQL-запрос
                    with connection.cursor() as cursor:
                        create = """
                            CREATE OR REPLACE FUNCTION count_estimate(query text) RETURNS integer AS $$
                            DECLARE
                              rec   record;
                              rows  integer;
                            BEGIN
                              FOR rec IN EXECUTE 'EXPLAIN ' || query LOOP
                                rows := substring(rec."QUERY PLAN" FROM ' rows=([[:digit:]]+)');
                                EXIT WHEN rows IS NOT NULL;
                              END LOOP;
                              RETURN rows;
                            END;
                            $$ LANGUAGE plpgsql VOLATILE STRICT;
                        """
                        cursor.execute(create)
                        cursor.execute("SELECT count_estimate(%s)", [query])
                        result = cursor.fetchone()
                        count = result[0] if result else 0
                        self._count = IntEstimate(count)
            else:
                self._count = estimate
        except (AttributeError, TypeError):
            # AttributeError if object_list has no count() method.
            # TypeError if object_list.count() requires arguments
            # (i.e. is of type list).
            self._count = len(self.object_list)
        return self._count
