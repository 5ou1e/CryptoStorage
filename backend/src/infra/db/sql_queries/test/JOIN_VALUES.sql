EXPLAIN ANALYZE
SELECT wt.wallet_id, COUNT(*) AS num_tokens
FROM wallet_token wt
JOIN (VALUES 
    ('12fcba69-d8ec-11ef-b944-08bfb8a414f6'::uuid),
    ('12fcba6e-d8ec-11ef-8951-08bfb8a414f6'::uuid),
    ('0e60dab5-d8ec-11ef-9618-08bfb8a414f6'::uuid)
) AS sw(id) ON wt.wallet_id = sw.id
GROUP BY wt.wallet_id;