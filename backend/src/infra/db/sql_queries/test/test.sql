BEGIN;
CREATE TEMPORARY TABLE aggregated_stats AS (
WITH selected_wallets AS (
	SELECT id
	FROM wallet
	WHERE stats_check_in_process = FALSE
	ORDER BY last_stats_check NULLS FIRST
	LIMIT 1000
)
SELECT
	wallet_id,
	-- Аггрегация для winrate и процентов
	COUNT(CASE WHEN total_buys_count > 0 AND total_profit_usd >= 0 THEN 1 ELSE NULL END) / 
		NULLIF(COUNT(CASE WHEN total_buys_count > 0 THEN 1 ELSE NULL END), 0) * 100 AS winrate_all,

	-- Основные суммы и количества
	SUM(total_buy_amount_usd) AS total_token_buy_amount_usd_all,
	SUM(total_sell_amount_usd) AS total_token_sell_amount_usd_all,
	SUM(total_profit_usd) AS total_profit_usd_all,
	SUM(total_profit_usd) / NULLIF(SUM(total_buy_amount_usd), 0) * 100 AS total_profit_multiplier_all,

	COUNT(*) AS total_token_all,
	SUM(total_buys_count) AS total_token_buys_all,
	SUM(total_sales_count) AS total_token_sales_all,

	-- Данные по токенам с покупкой и продажей
	COUNT(CASE WHEN total_buys_count > 0 AND total_sales_count > 0 THEN 1 ELSE NULL END) AS token_with_buy_and_sell_all,
	COUNT(CASE WHEN total_buys_count > 0 THEN 1 ELSE NULL END) AS token_with_buy_all,
	COUNT(CASE WHEN total_sales_count > 0 AND total_buys_count = 0 THEN 1 ELSE NULL END) AS token_sell_without_buy_all,
	COUNT(CASE WHEN total_buys_count > 0 AND total_sales_count = 0 THEN 1 ELSE NULL END) AS token_buy_without_sell_all,
	COUNT(CASE WHEN total_sell_amount_token > total_buy_amount_token THEN 1 ELSE NULL END) AS token_with_sell_amount_gt_buy_amount_all,

	-- Дополнительные расчеты для статистики
	SUM(first_buy_price_usd) / NULLIF(COUNT(CASE WHEN total_buys_count > 0 THEN 1 ELSE NULL END), 0) AS token_first_buy_avg_price_usd_all,
	PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY first_buy_price_usd) AS token_first_buy_median_price_usd_all,
	SUM(total_buy_amount_usd) / NULLIF(COUNT(CASE WHEN total_buys_count > 0 THEN 1 ELSE NULL END), 0) AS token_avg_buy_amount_all,
	PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY total_buy_amount_usd) AS token_median_buy_amount_all,
	SUM(total_profit_usd) / NULLIF(COUNT(CASE WHEN total_buys_count > 0 THEN 1 ELSE NULL END), 0) AS token_avg_profit_usd_all,

	-- Время покупки и продажи
	AVG(first_buy_sell_duration) AS token_buy_sell_duration_avg_all,
	PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY first_buy_sell_duration) AS token_buy_sell_duration_median_all,

	-- Профиль прибыли
	COUNT(CASE WHEN total_buys_count > 0 AND total_profit_percent >= 500 THEN 1 ELSE NULL END) AS pnl_gt_5x_num_all,
	COUNT(CASE WHEN total_buys_count > 0 AND total_profit_percent >= 200 AND total_profit_percent < 500 THEN 1 ELSE NULL END) AS pnl_2x_5x_num_all,
	COUNT(CASE WHEN total_buys_count > 0 AND total_profit_percent < 200 AND total_profit_percent >= 0 THEN 1 ELSE NULL END) AS pnl_lt_2x_num_all,
	COUNT(CASE WHEN total_buys_count > 0 AND total_profit_percent <= -50 THEN 1 ELSE NULL END) AS pnl_lt_minus_dot5_num_all,
	COUNT(CASE WHEN total_buys_count > 0 AND total_profit_percent > -50 AND total_profit_percent <= 0 THEN 1 ELSE NULL END) AS pnl_minus_dot5_0x_num_all,

	-- Проценты прибыли
	COUNT(CASE WHEN total_buys_count > 0 AND total_profit_percent <= -50 THEN 1 ELSE NULL END) * 100 / NULLIF(COUNT(CASE WHEN total_buys_count > 0 THEN 1 ELSE NULL END), 0) AS pnl_lt_minus_dot5_percent_all,
	COUNT(CASE WHEN total_buys_count > 0 AND total_profit_percent > -50 AND total_profit_percent <= 0 THEN 1 ELSE NULL END) * 100 / NULLIF(COUNT(CASE WHEN total_buys_count > 0 THEN 1 ELSE NULL END), 0) AS pnl_minus_dot5_0x_percent_all,
	COUNT(CASE WHEN total_buys_count > 0 AND total_profit_percent < 200 AND total_profit_percent >= 0 THEN 1 ELSE NULL END) * 100 / NULLIF(COUNT(CASE WHEN total_buys_count > 0 THEN 1 ELSE NULL END), 0) AS pnl_lt_2x_percent_all,
	COUNT(CASE WHEN total_buys_count > 0 AND total_profit_percent >= 200 AND total_profit_percent < 500 THEN 1 ELSE NULL END) * 100 / NULLIF(COUNT(CASE WHEN total_buys_count > 0 THEN 1 ELSE NULL END), 0) AS pnl_2x_5x_percent_all,
	COUNT(CASE WHEN total_buys_count > 0 AND total_profit_percent >= 500 THEN 1 ELSE NULL END) * 100 / NULLIF(COUNT(CASE WHEN total_buys_count > 0 THEN 1 ELSE NULL END), 0) AS pnl_gt_5x_percent_all,


	-- Процент побед (winrate) за последние 7 дней
	COUNT(CASE WHEN to_timestamp(last_activity_timestamp) >= NOW() - INTERVAL '7 days' AND total_buys_count > 0 AND total_profit_usd >= 0 THEN 1 ELSE NULL END) / 
		NULLIF(COUNT(CASE WHEN to_timestamp(last_activity_timestamp) >= NOW() - INTERVAL '7 days' AND total_buys_count > 0 THEN 1 ELSE NULL END), 0) * 100 AS winrate_7d,

	-- Основные суммы и количества за 7 дней
	SUM(CASE WHEN to_timestamp(last_activity_timestamp) >= NOW() - INTERVAL '7 days' THEN total_buy_amount_usd ELSE 0 END) AS total_token_buy_amount_usd_7d,
	SUM(CASE WHEN to_timestamp(last_activity_timestamp) >= NOW() - INTERVAL '7 days' THEN total_sell_amount_usd ELSE 0 END) AS total_token_sell_amount_usd_7d,
	SUM(CASE WHEN to_timestamp(last_activity_timestamp) >= NOW() - INTERVAL '7 days' THEN total_profit_usd ELSE 0 END) AS total_profit_usd_7d,
	SUM(CASE WHEN to_timestamp(last_activity_timestamp) >= NOW() - INTERVAL '7 days' THEN total_profit_usd ELSE 0 END) / 
		NULLIF(SUM(CASE WHEN to_timestamp(last_activity_timestamp) >= NOW() - INTERVAL '7 days' THEN total_buy_amount_usd ELSE 0 END), 0) * 100 AS total_profit_multiplier_7d,

	-- Количественные данные за последние 7 дней
	COUNT(CASE WHEN to_timestamp(last_activity_timestamp) >= NOW() - INTERVAL '7 days' THEN 1 ELSE NULL END) AS total_token_7d,
	SUM(CASE WHEN to_timestamp(last_activity_timestamp) >= NOW() - INTERVAL '7 days' THEN total_buys_count ELSE 0 END) AS total_token_buys_7d,
	SUM(CASE WHEN to_timestamp(last_activity_timestamp) >= NOW() - INTERVAL '7 days' THEN total_sales_count ELSE 0 END) AS total_token_sales_7d,

	-- Данные по токенам с покупкой и продажей за 7 дней
	COUNT(CASE WHEN to_timestamp(last_activity_timestamp) >= NOW() - INTERVAL '7 days' AND total_buys_count > 0 AND total_sales_count > 0 THEN 1 ELSE NULL END) AS token_with_buy_and_sell_7d,
	COUNT(CASE WHEN to_timestamp(last_activity_timestamp) >= NOW() - INTERVAL '7 days' AND total_buys_count > 0 THEN 1 ELSE NULL END) AS token_with_buy_7d,
	COUNT(CASE WHEN to_timestamp(last_activity_timestamp) >= NOW() - INTERVAL '7 days' AND total_sales_count > 0 AND total_buys_count = 0 THEN 1 ELSE NULL END) AS token_sell_without_buy_7d,
	COUNT(CASE WHEN to_timestamp(last_activity_timestamp) >= NOW() - INTERVAL '7 days' AND total_buys_count > 0 AND total_sales_count = 0 THEN 1 ELSE NULL END) AS token_buy_without_sell_7d,
	COUNT(CASE WHEN to_timestamp(last_activity_timestamp) >= NOW() - INTERVAL '7 days' AND total_sell_amount_token > total_buy_amount_token THEN 1 ELSE NULL END) AS token_with_sell_amount_gt_buy_amount_7d,

	-- Дополнительные расчеты для статистики за 7 дней
	SUM(CASE WHEN to_timestamp(last_activity_timestamp) >= NOW() - INTERVAL '7 days' THEN first_buy_price_usd ELSE 0 END) / 
		NULLIF(COUNT(CASE WHEN to_timestamp(last_activity_timestamp) >= NOW() - INTERVAL '7 days' AND total_buys_count > 0 THEN 1 ELSE NULL END), 0) AS token_first_buy_avg_price_usd_7d,
	PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY CASE WHEN to_timestamp(last_activity_timestamp) >= NOW() - INTERVAL '7 days' THEN first_buy_price_usd END) AS token_first_buy_median_price_usd_7d,
	SUM(CASE WHEN to_timestamp(last_activity_timestamp) >= NOW() - INTERVAL '7 days' THEN total_buy_amount_usd ELSE 0 END) / 
		NULLIF(COUNT(CASE WHEN to_timestamp(last_activity_timestamp) >= NOW() - INTERVAL '7 days' AND total_buys_count > 0 THEN 1 ELSE NULL END), 0) AS token_avg_buy_amount_7d,
	PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY CASE WHEN to_timestamp(last_activity_timestamp) >= NOW() - INTERVAL '7 days' THEN total_buy_amount_usd END) AS token_median_buy_amount_7d,
	SUM(CASE WHEN to_timestamp(last_activity_timestamp) >= NOW() - INTERVAL '7 days' THEN total_profit_usd ELSE 0 END) / 
		NULLIF(COUNT(CASE WHEN to_timestamp(last_activity_timestamp) >= NOW() - INTERVAL '7 days' AND total_buys_count > 0 THEN 1 ELSE NULL END), 0) AS token_avg_profit_usd_7d,

	-- Время покупки и продажи за 7 дней
	AVG(CASE WHEN to_timestamp(last_activity_timestamp) >= NOW() - INTERVAL '7 days' THEN first_buy_sell_duration ELSE NULL END) AS token_buy_sell_duration_avg_7d,
	PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY CASE WHEN to_timestamp(last_activity_timestamp) >= NOW() - INTERVAL '7 days' THEN first_buy_sell_duration END) AS token_buy_sell_duration_median_7d,

	-- Профиль прибыли за 7 дней
	COUNT(CASE WHEN to_timestamp(last_activity_timestamp) >= NOW() - INTERVAL '7 days' AND total_buys_count > 0 AND total_profit_percent >= 500 THEN 1 ELSE NULL END) AS pnl_gt_5x_num_7d,
	COUNT(CASE WHEN to_timestamp(last_activity_timestamp) >= NOW() - INTERVAL '7 days' AND total_buys_count > 0 AND total_profit_percent >= 200 AND total_profit_percent < 500 THEN 1 ELSE NULL END) AS pnl_2x_5x_num_7d,
	COUNT(CASE WHEN to_timestamp(last_activity_timestamp) >= NOW() - INTERVAL '7 days' AND total_buys_count > 0 AND total_profit_percent < 200 AND total_profit_percent >= 0 THEN 1 ELSE NULL END) AS pnl_lt_2x_num_7d,
	COUNT(CASE WHEN to_timestamp(last_activity_timestamp) >= NOW() - INTERVAL '7 days' AND total_buys_count > 0 AND total_profit_percent <= -50 THEN 1 ELSE NULL END) AS pnl_lt_minus_dot5_num_7d,
	COUNT(CASE WHEN to_timestamp(last_activity_timestamp) >= NOW() - INTERVAL '7 days' AND total_buys_count > 0 AND total_profit_percent > -50 AND total_profit_percent <= 0 THEN 1 ELSE NULL END) AS pnl_minus_dot5_0x_num_7d,

	-- Проценты прибыли за 7 дней
	COUNT(CASE WHEN to_timestamp(last_activity_timestamp) >= NOW() - INTERVAL '7 days' AND total_buys_count > 0 AND total_profit_percent <= -50 THEN 1 ELSE NULL END) * 100 / 
		NULLIF(COUNT(CASE WHEN to_timestamp(last_activity_timestamp) >= NOW() - INTERVAL '7 days' AND total_buys_count > 0 THEN 1 ELSE NULL END), 0) AS pnl_lt_minus_dot5_percent_7d,
	COUNT(CASE WHEN to_timestamp(last_activity_timestamp) >= NOW() - INTERVAL '7 days' AND total_buys_count > 0 AND total_profit_percent > -50 AND total_profit_percent <= 0 THEN 1 ELSE NULL END) * 100 / 
		NULLIF(COUNT(CASE WHEN to_timestamp(last_activity_timestamp) >= NOW() - INTERVAL '7 days' AND total_buys_count > 0 THEN 1 ELSE NULL END), 0) AS pnl_minus_dot5_0x_percent_7d,
	COUNT(CASE WHEN to_timestamp(last_activity_timestamp) >= NOW() - INTERVAL '7 days' AND total_buys_count > 0 AND total_profit_percent < 200 AND total_profit_percent >= 0 THEN 1 ELSE NULL END) * 100 / 
		NULLIF(COUNT(CASE WHEN to_timestamp(last_activity_timestamp) >= NOW() - INTERVAL '7 days' AND total_buys_count > 0 THEN 1 ELSE NULL END), 0) AS pnl_lt_2x_percent_7d,
	COUNT(CASE WHEN to_timestamp(last_activity_timestamp) >= NOW() - INTERVAL '7 days' AND total_buys_count > 0 AND total_profit_percent >= 200 AND total_profit_percent < 500 THEN 1 ELSE NULL END) * 100 / 
		NULLIF(COUNT(CASE WHEN to_timestamp(last_activity_timestamp) >= NOW() - INTERVAL '7 days' AND total_buys_count > 0 THEN 1 ELSE NULL END), 0) AS pnl_2x_5x_percent_7d,
	COUNT(CASE WHEN to_timestamp(last_activity_timestamp) >= NOW() - INTERVAL '7 days' AND total_buys_count > 0 AND total_profit_percent >= 500 THEN 1 ELSE NULL END) * 100 / 
		NULLIF(COUNT(CASE WHEN to_timestamp(last_activity_timestamp) >= NOW() - INTERVAL '7 days' AND total_buys_count > 0 THEN 1 ELSE NULL END), 0) AS pnl_gt_5x_percent_7d,
	
	
	-- Процент побед (winrate) за последние 30 дней
	COUNT(CASE WHEN to_timestamp(last_activity_timestamp) >= NOW() - INTERVAL '30 days' AND total_buys_count > 0 AND total_profit_usd >= 0 THEN 1 ELSE NULL END) / 
		NULLIF(COUNT(CASE WHEN to_timestamp(last_activity_timestamp) >= NOW() - INTERVAL '30 days' AND total_buys_count > 0 THEN 1 ELSE NULL END), 0) * 100 AS winrate_30d,

	-- Основные суммы и количества за 30 дней
	SUM(CASE WHEN to_timestamp(last_activity_timestamp) >= NOW() - INTERVAL '30 days' THEN total_buy_amount_usd ELSE 0 END) AS total_token_buy_amount_usd_30d,
	SUM(CASE WHEN to_timestamp(last_activity_timestamp) >= NOW() - INTERVAL '30 days' THEN total_sell_amount_usd ELSE 0 END) AS total_token_sell_amount_usd_30d,
	SUM(CASE WHEN to_timestamp(last_activity_timestamp) >= NOW() - INTERVAL '30 days' THEN total_profit_usd ELSE 0 END) AS total_profit_usd_30d,
	SUM(CASE WHEN to_timestamp(last_activity_timestamp) >= NOW() - INTERVAL '30 days' THEN total_profit_usd ELSE 0 END) / 
		NULLIF(SUM(CASE WHEN to_timestamp(last_activity_timestamp) >= NOW() - INTERVAL '30 days' THEN total_buy_amount_usd ELSE 0 END), 0) * 100 AS total_profit_multiplier_30d,

	-- Количественные данные за последние 30 дней
	COUNT(CASE WHEN to_timestamp(last_activity_timestamp) >= NOW() - INTERVAL '30 days' THEN 1 ELSE NULL END) AS total_token_30d,
	SUM(CASE WHEN to_timestamp(last_activity_timestamp) >= NOW() - INTERVAL '30 days' THEN total_buys_count ELSE 0 END) AS total_token_buys_30d,
	SUM(CASE WHEN to_timestamp(last_activity_timestamp) >= NOW() - INTERVAL '30 days' THEN total_sales_count ELSE 0 END) AS total_token_sales_30d,

	-- Данные по токенам с покупкой и продажей за 30 дней
	COUNT(CASE WHEN to_timestamp(last_activity_timestamp) >= NOW() - INTERVAL '30 days' AND total_buys_count > 0 AND total_sales_count > 0 THEN 1 ELSE NULL END) AS token_with_buy_and_sell_30d,
	COUNT(CASE WHEN to_timestamp(last_activity_timestamp) >= NOW() - INTERVAL '30 days' AND total_buys_count > 0 THEN 1 ELSE NULL END) AS token_with_buy_30d,
	COUNT(CASE WHEN to_timestamp(last_activity_timestamp) >= NOW() - INTERVAL '30 days' AND total_sales_count > 0 AND total_buys_count = 0 THEN 1 ELSE NULL END) AS token_sell_without_buy_30d,
	COUNT(CASE WHEN to_timestamp(last_activity_timestamp) >= NOW() - INTERVAL '30 days' AND total_buys_count > 0 AND total_sales_count = 0 THEN 1 ELSE NULL END) AS token_buy_without_sell_30d,
	COUNT(CASE WHEN to_timestamp(last_activity_timestamp) >= NOW() - INTERVAL '30 days' AND total_sell_amount_token > total_buy_amount_token THEN 1 ELSE NULL END) AS token_with_sell_amount_gt_buy_amount_30d,

	-- Дополнительные расчеты для статистики за 30 дней
	SUM(CASE WHEN to_timestamp(last_activity_timestamp) >= NOW() - INTERVAL '30 days' THEN first_buy_price_usd ELSE 0 END) / 
		NULLIF(COUNT(CASE WHEN to_timestamp(last_activity_timestamp) >= NOW() - INTERVAL '30 days' AND total_buys_count > 0 THEN 1 ELSE NULL END), 0) AS token_first_buy_avg_price_usd_30d,
	PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY CASE WHEN to_timestamp(last_activity_timestamp) >= NOW() - INTERVAL '30 days' THEN first_buy_price_usd END) AS token_first_buy_median_price_usd_30d,
	SUM(CASE WHEN to_timestamp(last_activity_timestamp) >= NOW() - INTERVAL '30 days' THEN total_buy_amount_usd ELSE 0 END) / 
		NULLIF(COUNT(CASE WHEN to_timestamp(last_activity_timestamp) >= NOW() - INTERVAL '30 days' AND total_buys_count > 0 THEN 1 ELSE NULL END), 0) AS token_avg_buy_amount_30d,
	PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY CASE WHEN to_timestamp(last_activity_timestamp) >= NOW() - INTERVAL '30 days' THEN total_buy_amount_usd END) AS token_median_buy_amount_30d,
	SUM(CASE WHEN to_timestamp(last_activity_timestamp) >= NOW() - INTERVAL '30 days' THEN total_profit_usd ELSE 0 END) / 
		NULLIF(COUNT(CASE WHEN to_timestamp(last_activity_timestamp) >= NOW() - INTERVAL '30 days' AND total_buys_count > 0 THEN 1 ELSE NULL END), 0) AS token_avg_profit_usd_30d,

	-- Время покупки и продажи за 30 дней
	AVG(CASE WHEN to_timestamp(last_activity_timestamp) >= NOW() - INTERVAL '30 days' THEN first_buy_sell_duration ELSE NULL END) AS token_buy_sell_duration_avg_30d,
	PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY CASE WHEN to_timestamp(last_activity_timestamp) >= NOW() - INTERVAL '30 days' THEN first_buy_sell_duration END) AS token_buy_sell_duration_median_30d,

	-- Профиль прибыли за 30 дней
	COUNT(CASE WHEN to_timestamp(last_activity_timestamp) >= NOW() - INTERVAL '30 days' AND total_buys_count > 0 AND total_profit_percent >= 500 THEN 1 ELSE NULL END) AS pnl_gt_5x_num_30d,
	COUNT(CASE WHEN to_timestamp(last_activity_timestamp) >= NOW() - INTERVAL '30 days' AND total_buys_count > 0 AND total_profit_percent >= 200 AND total_profit_percent < 500 THEN 1 ELSE NULL END) AS pnl_2x_5x_num_30d,
	COUNT(CASE WHEN to_timestamp(last_activity_timestamp) >= NOW() - INTERVAL '30 days' AND total_buys_count > 0 AND total_profit_percent < 200 AND total_profit_percent >= 0 THEN 1 ELSE NULL END) AS pnl_lt_2x_num_30d,
	COUNT(CASE WHEN to_timestamp(last_activity_timestamp) >= NOW() - INTERVAL '30 days' AND total_buys_count > 0 AND total_profit_percent <= -50 THEN 1 ELSE NULL END) AS pnl_lt_minus_dot5_num_30d,
	COUNT(CASE WHEN to_timestamp(last_activity_timestamp) >= NOW() - INTERVAL '30 days' AND total_buys_count > 0 AND total_profit_percent > -50 AND total_profit_percent <= 0 THEN 1 ELSE NULL END) AS pnl_minus_dot5_0x_num_30d,

	-- Проценты прибыли за 30 дней
	COUNT(CASE WHEN to_timestamp(last_activity_timestamp) >= NOW() - INTERVAL '30 days' AND total_buys_count > 0 AND total_profit_percent <= -50 THEN 1 ELSE NULL END) * 100 / 
		NULLIF(COUNT(CASE WHEN to_timestamp(last_activity_timestamp) >= NOW() - INTERVAL '30 days' AND total_buys_count > 0 THEN 1 ELSE NULL END), 0) AS pnl_lt_minus_dot5_percent_30d,
	COUNT(CASE WHEN to_timestamp(last_activity_timestamp) >= NOW() - INTERVAL '30 days' AND total_buys_count > 0 AND total_profit_percent > -50 AND total_profit_percent <= 0 THEN 1 ELSE NULL END) * 100 / 
		NULLIF(COUNT(CASE WHEN to_timestamp(last_activity_timestamp) >= NOW() - INTERVAL '30 days' AND total_buys_count > 0 THEN 1 ELSE NULL END), 0) AS pnl_minus_dot5_0x_percent_30d,
	COUNT(CASE WHEN to_timestamp(last_activity_timestamp) >= NOW() - INTERVAL '30 days' AND total_buys_count > 0 AND total_profit_percent < 200 AND total_profit_percent >= 0 THEN 1 ELSE NULL END) * 100 / 
		NULLIF(COUNT(CASE WHEN to_timestamp(last_activity_timestamp) >= NOW() - INTERVAL '30 days' AND total_buys_count > 0 THEN 1 ELSE NULL END), 0) AS pnl_lt_2x_percent_30d,
	COUNT(CASE WHEN to_timestamp(last_activity_timestamp) >= NOW() - INTERVAL '30 days' AND total_buys_count > 0 AND total_profit_percent >= 200 AND total_profit_percent < 500 THEN 1 ELSE NULL END) * 100 / 
		NULLIF(COUNT(CASE WHEN to_timestamp(last_activity_timestamp) >= NOW() - INTERVAL '30 days' AND total_buys_count > 0 THEN 1 ELSE NULL END), 0) AS pnl_2x_5x_percent_30d,
	COUNT(CASE WHEN to_timestamp(last_activity_timestamp) >= NOW() - INTERVAL '30 days' AND total_buys_count > 0 AND total_profit_percent >= 500 THEN 1 ELSE NULL END) * 100 / 
		NULLIF(COUNT(CASE WHEN to_timestamp(last_activity_timestamp) >= NOW() - INTERVAL '30 days' AND total_buys_count > 0 THEN 1 ELSE NULL END), 0) AS pnl_gt_5x_percent_30d
	
	
	FROM wallet_token_statistic
    WHERE wallet_id IN (SELECT id FROM selected_wallets)
    GROUP BY wallet_id
);

-- Обновление для всех данных
UPDATE wallet_period_statistic_all ws
SET
    winrate = aggregated_stats.winrate_all,
    total_token_buy_amount_usd = aggregated_stats.total_token_buy_amount_usd_all,
    total_token_sell_amount_usd = aggregated_stats.total_token_sell_amount_usd_all,
    total_profit_usd = aggregated_stats.total_profit_usd_all,
    total_profit_multiplier = aggregated_stats.total_profit_multiplier_all,
    total_token = aggregated_stats.total_token_all,
    total_token_buys = aggregated_stats.total_token_buys_all,
    total_token_sales = aggregated_stats.total_token_sales_all,
    token_with_buy_and_sell = aggregated_stats.token_with_buy_and_sell_all,
    token_with_buy = aggregated_stats.token_with_buy_all,
    token_sell_without_buy = aggregated_stats.token_sell_without_buy_all,
    token_buy_without_sell = aggregated_stats.token_buy_without_sell_all,
    token_with_sell_amount_gt_buy_amount = aggregated_stats.token_with_sell_amount_gt_buy_amount_all,
    token_avg_buy_amount = aggregated_stats.token_avg_buy_amount_all,
    token_median_buy_amount = aggregated_stats.token_median_buy_amount_all,
    token_first_buy_avg_price_usd = aggregated_stats.token_first_buy_avg_price_usd_all,
    token_first_buy_median_price_usd = aggregated_stats.token_first_buy_median_price_usd_all,
    token_avg_profit_usd = aggregated_stats.token_avg_profit_usd_all,
    token_buy_sell_duration_avg = aggregated_stats.token_buy_sell_duration_avg_all,
    token_buy_sell_duration_median = aggregated_stats.token_buy_sell_duration_median_all,
    pnl_lt_minus_dot5_num = aggregated_stats.pnl_lt_minus_dot5_num_all,
    pnl_minus_dot5_0x_num = aggregated_stats.pnl_minus_dot5_0x_num_all,
    pnl_lt_2x_num = aggregated_stats.pnl_lt_2x_num_all,
    pnl_2x_5x_num = aggregated_stats.pnl_2x_5x_num_all,
    pnl_gt_5x_num = aggregated_stats.pnl_gt_5x_num_all,
    pnl_lt_minus_dot5_percent = aggregated_stats.pnl_lt_minus_dot5_percent_all,
    pnl_minus_dot5_0x_percent = aggregated_stats.pnl_minus_dot5_0x_percent_all,
    pnl_lt_2x_percent = aggregated_stats.pnl_lt_2x_percent_all,
    pnl_2x_5x_percent = aggregated_stats.pnl_2x_5x_percent_all,
    pnl_gt_5x_percent = aggregated_stats.pnl_gt_5x_percent_all,
    updated_at = NOW()
FROM aggregated_stats
WHERE ws.wallet_id = aggregated_stats.wallet_id;

UPDATE wallet_period_statistic_7d ws
SET
    winrate = aggregated_stats.winrate_7d,
    total_token_buy_amount_usd = aggregated_stats.total_token_buy_amount_usd_7d,
    total_token_sell_amount_usd = aggregated_stats.total_token_sell_amount_usd_7d,
    total_profit_usd = aggregated_stats.total_profit_usd_7d,
    total_profit_multiplier = aggregated_stats.total_profit_multiplier_7d,
    total_token = aggregated_stats.total_token_7d,
    total_token_buys = aggregated_stats.total_token_buys_7d,
    total_token_sales = aggregated_stats.total_token_sales_7d,
    token_with_buy_and_sell = aggregated_stats.token_with_buy_and_sell_7d,
    token_with_buy = aggregated_stats.token_with_buy_7d,
    token_sell_without_buy = aggregated_stats.token_sell_without_buy_7d,
    token_buy_without_sell = aggregated_stats.token_buy_without_sell_7d,
    token_with_sell_amount_gt_buy_amount = aggregated_stats.token_with_sell_amount_gt_buy_amount_7d,
    token_avg_buy_amount = aggregated_stats.token_avg_buy_amount_7d,
    token_median_buy_amount = aggregated_stats.token_median_buy_amount_7d,
    token_first_buy_avg_price_usd = aggregated_stats.token_first_buy_avg_price_usd_7d,
    token_first_buy_median_price_usd = aggregated_stats.token_first_buy_median_price_usd_7d,
    token_avg_profit_usd = aggregated_stats.token_avg_profit_usd_7d,
    token_buy_sell_duration_avg = aggregated_stats.token_buy_sell_duration_avg_7d,
    token_buy_sell_duration_median = aggregated_stats.token_buy_sell_duration_median_7d,
    pnl_lt_minus_dot5_num = aggregated_stats.pnl_lt_minus_dot5_num_7d,
    pnl_minus_dot5_0x_num = aggregated_stats.pnl_minus_dot5_0x_num_7d,
    pnl_lt_2x_num = aggregated_stats.pnl_lt_2x_num_7d,
    pnl_2x_5x_num = aggregated_stats.pnl_2x_5x_num_7d,
    pnl_gt_5x_num = aggregated_stats.pnl_gt_5x_num_7d,
    pnl_lt_minus_dot5_percent = aggregated_stats.pnl_lt_minus_dot5_percent_7d,
    pnl_minus_dot5_0x_percent = aggregated_stats.pnl_minus_dot5_0x_percent_7d,
    pnl_lt_2x_percent = aggregated_stats.pnl_lt_2x_percent_7d,
    pnl_2x_5x_percent = aggregated_stats.pnl_2x_5x_percent_7d,
    pnl_gt_5x_percent = aggregated_stats.pnl_gt_5x_percent_7d,
    updated_at = NOW()
FROM aggregated_stats
WHERE ws.wallet_id = aggregated_stats.wallet_id;

UPDATE wallet_period_statistic_30d ws
SET
    winrate = aggregated_stats.winrate_30d,
    total_token_buy_amount_usd = aggregated_stats.total_token_buy_amount_usd_30d,
    total_token_sell_amount_usd = aggregated_stats.total_token_sell_amount_usd_30d,
    total_profit_usd = aggregated_stats.total_profit_usd_30d,
    total_profit_multiplier = aggregated_stats.total_profit_multiplier_30d,
    total_token = aggregated_stats.total_token_30d,
    total_token_buys = aggregated_stats.total_token_buys_30d,
    total_token_sales = aggregated_stats.total_token_sales_30d,
    token_with_buy_and_sell = aggregated_stats.token_with_buy_and_sell_30d,
    token_with_buy = aggregated_stats.token_with_buy_30d,
    token_sell_without_buy = aggregated_stats.token_sell_without_buy_30d,
    token_buy_without_sell = aggregated_stats.token_buy_without_sell_30d,
    token_with_sell_amount_gt_buy_amount = aggregated_stats.token_with_sell_amount_gt_buy_amount_30d,
    token_avg_buy_amount = aggregated_stats.token_avg_buy_amount_30d,
    token_median_buy_amount = aggregated_stats.token_median_buy_amount_30d,
    token_first_buy_avg_price_usd = aggregated_stats.token_first_buy_avg_price_usd_30d,
    token_first_buy_median_price_usd = aggregated_stats.token_first_buy_median_price_usd_30d,
    token_avg_profit_usd = aggregated_stats.token_avg_profit_usd_30d,
    token_buy_sell_duration_avg = aggregated_stats.token_buy_sell_duration_avg_30d,
    token_buy_sell_duration_median = aggregated_stats.token_buy_sell_duration_median_30d,
    pnl_lt_minus_dot5_num = aggregated_stats.pnl_lt_minus_dot5_num_30d,
    pnl_minus_dot5_0x_num = aggregated_stats.pnl_minus_dot5_0x_num_30d,
    pnl_lt_2x_num = aggregated_stats.pnl_lt_2x_num_30d,
    pnl_2x_5x_num = aggregated_stats.pnl_2x_5x_num_30d,
    pnl_gt_5x_num = aggregated_stats.pnl_gt_5x_num_30d,
    pnl_lt_minus_dot5_percent = aggregated_stats.pnl_lt_minus_dot5_percent_30d,
    pnl_minus_dot5_0x_percent = aggregated_stats.pnl_minus_dot5_0x_percent_30d,
    pnl_lt_2x_percent = aggregated_stats.pnl_lt_2x_percent_30d,
    pnl_2x_5x_percent = aggregated_stats.pnl_2x_5x_percent_30d,
    pnl_gt_5x_percent = aggregated_stats.pnl_gt_5x_percent_30d,
    updated_at = NOW()
FROM aggregated_stats
WHERE ws.wallet_id = aggregated_stats.wallet_id;


DROP TABLE aggregated_stats;

COMMIT;
