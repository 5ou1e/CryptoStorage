import textwrap

# 1. если активность была в последние 31 дней. (чтобы чекнулась хотя бы раз статистика за месяц для старых)
GET_WALLETS_FOR_UPDATE_STATS = textwrap.dedent(
    """\
    SELECT
      *
    FROM
      wallet
    WHERE
      last_activity_timestamp > now() - '31 days'::interval
    ORDER BY
      last_stats_check NULLS FIRST
    LIMIT {count};
"""
)


GET_WALLETS_FOR_UPDATE_STATS_ALL = textwrap.dedent(
    """\
    SELECT *
    FROM wallet
    ORDER BY last_stats_check NULLS FIRST
    LIMIT {count}
"""
)

# Создает функцию coun_estimate для подсчета примерного кол-ва строк для запросов с фильтрами
CREATE_FUNC_COUNT_ESTIMATE = """
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

GET_COUNT_ESTIMATE_WITH_FUNC = "SELECT count_estimate('{query}')"

GET_COUNT_ESTIMATE_FULL = """
    SELECT reltuples::bigint AS count_estimate
    FROM pg_class
    WHERE relname = '{table_name}'
"""
