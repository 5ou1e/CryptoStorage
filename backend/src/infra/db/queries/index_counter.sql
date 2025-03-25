SELECT relname, indexrelname, idx_scan
FROM   pg_catalog.pg_stat_user_indexes
WHERE  schemaname = 'public';