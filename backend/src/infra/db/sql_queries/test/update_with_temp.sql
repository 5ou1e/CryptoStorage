BEGIN;

-- Создание временной таблицы для хранения агрегированных данных
CREATE TEMPORARY TABLE temp_aggregated_stats1 AS
WITH selected_wallets AS (
    SELECT id
    FROM wallet
    WHERE stats_check_in_process = FALSE
    ORDER BY last_stats_check NULLS FIRST
    LIMIT 100000  -- Ограничение на 10000 кошельков
)
SELECT
    wallet_id,
    COUNT(*) AS total_token_all
FROM wallet_token_statistic
WHERE wallet_id IN (SELECT id FROM selected_wallets)
GROUP BY wallet_id;

-- Обновление для всех данных
UPDATE wallet_period_statistic_all ws
SET
    total_token = temp_aggregated_stats.total_token_all,
    updated_at = NOW()
FROM temp_aggregated_stats
WHERE ws.wallet_id = temp_aggregated_stats.wallet_id;

-- Обновление для данных за 7 дней
UPDATE wallet_period_statistic_7d ws
SET
    total_token = temp_aggregated_stats.total_token_all,
    updated_at = NOW()
FROM temp_aggregated_stats
WHERE ws.wallet_id = temp_aggregated_stats.wallet_id;

-- Удаление временной таблицы
DROP TABLE temp_aggregated_stats1;

COMMIT;