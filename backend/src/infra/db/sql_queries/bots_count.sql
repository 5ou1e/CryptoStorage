SELECT 
    COUNT(CASE WHEN is_scammer = TRUE THEN 1 END) AS scammer_count,
    COUNT(CASE WHEN is_bot = TRUE THEN 1 END) AS bot_count
FROM wallet;
