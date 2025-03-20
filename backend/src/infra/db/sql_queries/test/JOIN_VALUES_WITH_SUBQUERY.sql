EXPLAIN ANALYZE
SELECT COUNT(*)
FROM wallet_token AS t
JOIN (
    SELECT id FROM wallet ORDER BY last_stats_check NULLS first LIMIT 50000
) AS subquery ON t.wallet_id = subquery.id;