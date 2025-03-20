EXPLAIN ANALYZE
SELECT *
FROM wallet_token
WHERE
wallet_id IN (
	('12fcba69-d8ec-11ef-b944-08bfb8a414f6'),
	('12fcba6e-d8ec-11ef-8951-08bfb8a414f6'),
	('0e60dab5-d8ec-11ef-9618-08bfb8a414f6')
)
