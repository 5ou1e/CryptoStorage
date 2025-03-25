SELECT 
    COUNT(*) * 1.0 / EXTRACT(EPOCH FROM (MAX(last_stats_check) - MIN(last_stats_check)) / 60) AS avg_checks_per_minute
FROM wallet
WHERE last_stats_check >= '2025-02-24 18:40:00';