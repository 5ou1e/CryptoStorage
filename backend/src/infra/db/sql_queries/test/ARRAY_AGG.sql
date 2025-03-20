EXPLAIN ANALYZE
SELECT COUNT(*)
FROM wallet_token as t
JOIN UNNEST(
    (SELECT array_agg(id) 
FROM (SELECT id FROM wallet ORDER BY id LIMIT 30000) as qwe)
) AS subquery(val) ON t.wallet_id = subquery.val
