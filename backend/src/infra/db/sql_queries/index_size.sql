SELECT 
    indexrelid::regclass AS index_name, 
    pg_size_pretty(pg_relation_size(indexrelid)) AS index_size
FROM 
    pg_stat_user_indexes
WHERE 
    relname = 'swap'
ORDER BY 
    pg_relation_size(indexrelid) DESC;
