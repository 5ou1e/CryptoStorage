WITH selectedwallets AS (
  SELECT
    ws.wallet_id
  FROM
    wallet_statistic_all ws
  WHERE
    ws.total_token = 1
    AND ws.total_token_sales = 0
    AND ws.total_token_buy_amount_usd >= 5000
),
filteredwallettokens AS (
  SELECT
    wallet_id,
    token_id,
    wallets_count,
    t.address token_address
  FROM
    (
      SELECT
        wt.wallet_id,
        wt.token_id,
        count(*) OVER(PARTITION BY wt.token_id) wallets_count
      FROM
        wallet_token wt
      WHERE
        EXISTS(
          SELECT
            1
          FROM
            selectedwallets sw
          WHERE
            sw.wallet_id = wt.wallet_id
        )
    ) ft
    JOIN token t ON ft.token_id = t.id
  WHERE
    wallets_count >= 5
    AND NOT t.address IN (
      'J1toso1uCk3RLmjorhTtrVwY9HJ7X8V9yYac6Y7kGCPn',
      'mSoLzYCxHdYgdzU16g5QSh3i5K3z3KZK7ytfqcJm7So',
      'Bybit2vBJGhPF52GBdNaQfUJ6ZpThSgHBobjWZpLPb4B',
      'Dso1bDeDjCQxTrWHqUUi63oBvV7Mdm6WaobLbQ7gnPQ',
      'cbbtcf3aa214zXHbiAZQwf4122FBYbraNdFqgw4iMij',
      '5oVNBeEEQvYi1cX3ir8Dx5n1P7pdxydbGF2X4TxVusJm',
      'BPSoLzmLQn47EP5aa7jmFngRL8KC3TWAeAwXwZD8ip3P',
      'he1iusmfkpAdwvxLNGV8Y1iSbj4rUy6yMhEA3fotn9A',
      'So11111111111111111111111111111111111111112',
      '2Wu1g2ft7qZHfTpfzP3wLdfPeV1is4EwQ3CXBfRYAciD',
      '6p6xgHyF7AeE6TZkSmFsko444wqoP15icUSqi2jfGiPN',
      'Hg8bKz4mvs8KNj9zew1cEF9tDw1x2GViB4RFZjVEmfrD',
      'ABtJ6m5ooNbua9uT4XKSX34F79ZwCtT2FepENbpUYucd',
      '43VWkd99HjqkhFTZbWBpMpRhjG469nWa7x7uEsgSH7We',
      'RAPRz9fd87y9qcBGj1VVqUbbUM6DaBggSDA58zc3N2b',
      '9McvH6w97oewLmPxqQEoHUAv3u5iYMyQ9AeZZhguYf1T',
      'oreoU2P8bN6jkk3jbaiVxYnG1dCXcYxwhwyK9jSybcp',
      'MEFNBXixkEbait3xn9bkm8WsJzXtVsaJEn4c8Sam21u',
      'G7iK3prSzAA4vzcJWvsLUEsdCqzR7PnMzJV61vSdFSNW',
      '1Qf8gESP4i6CFNWerUSDdLKJ9U1LpqTYvjJ2MM4pain',
      '2b1kV6DkPAnxd5ixfnxCpjxmKwqjjaYmCZfHsFu24GXo',
      'hntyVP6YFm1Hg25TN9WGLqM12b8TQmcknKrdu1oxWux',
      'sSo14endRuUbvQaJS3dq36Q829a3A6BEfoeeRGJywEh',
      'ezSoL6fY1PVdJcJsUpe5CM3xkfmy3zoVCABybm5WtiC'
    )
)
SELECT
  ft.token_address,
  w.address wallet_address,
  ft.wallets_count wallets_count,
  round(wt.total_buy_amount_usd, 2) wallet_buy_amount_usd,
  round(wt.first_buy_price_usd, 8) wallet_first_buy_price_usd,
  wt.first_buy_timestamp wallet_first_buy_timestamp,
  lts.token_price_usd last_token_price,
  round(
    (
      lts.token_price_usd / nullif(wt.first_buy_price_usd, 0) -1
    ) * 100,
    0
  ) pumped_multiplier_percent,
  lts.timestamp last_token_swap_timestamp
FROM
  wallet_token wt
  JOIN filteredwallettokens ft ON wt.token_id = ft.token_id
  AND wt.wallet_id = ft.wallet_id
  JOIN wallet w ON wt.wallet_id = w.id
  LEFT JOIN LATERAL (
    SELECT
      s.token_id,
      round(
        s.price_usd * s.quote_amount / nullif(s.token_amount, 0),
        8
      ) token_price_usd,
      s.timestamp
    FROM
      swap s
    WHERE
      s.token_id = ft.token_id
    ORDER BY
      s.timestamp DESC
    LIMIT
      1
  ) lts ON TRUE
WHERE
  wt.first_buy_price_usd >= 0.0001
  AND wt.first_buy_price_usd < 0.01
ORDER BY
  max(
    round(
      (
        lts.token_price_usd / nullif(wt.first_buy_price_usd, 0) -1
      ) * 100,
      2
    )
  ) OVER(PARTITION BY ft.token_address) DESC,
  ft.token_address,
  wt.first_buy_timestamp;
