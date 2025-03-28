SELECT 
    pid,
    application_name,
	backend_start,
    xact_start,
    query_start,
    state,
    query

FROM 
    pg_stat_activity
WHERE
	state = 'active'
	AND
    pid <> pg_backend_pid()  -- Исключаем свой процесс
ORDER BY 
    query_start DESC;