import logging
from datetime import datetime, timedelta
from flipside import Flipside

from src.domain.constants import SOL_ADDRESS


def sql_get_swaps(
    start_time: datetime,
    end_time: datetime,
    blacklisted_tokens: set,
    offset: int = 0,
    limit: int | None = None,
):
    """SQL-запрос для получения swaps с Flipside-crypto"""
    if limit is None:
        limit = 100000
    query = f"""
        SELECT
            tx_id,
            FACT_SWAPS_JUPITER_SUMMARY_ID
        FROM
            solana.defi.fact_swaps_jupiter_summary
        WHERE
              BLOCK_TIMESTAMP >= '{start_time}'
              AND BLOCK_TIMESTAMP < '{end_time}'
              AND NOT (
                SWAP_FROM_MINT = '{SOL_ADDRESS}'
                OR SWAP_TO_MINT = '{SOL_ADDRESS}'
              )
            AND swapper IS NOT NULL
        ORDER BY FACT_SWAPS_JUPITER_SUMMARY_ID ASC
        LIMIT {limit} OFFSET {offset};
    """
    return query

#
# logging.basicConfig(level=logging.DEBUG)
# flipside = Flipside(
#     "17ac4677-856d-4a86-9c94-36b4e637393c",
#     "https://api-v2.flipsidecrypto.xyz",
# )
# query = sql_get_swaps(
#     datetime.now() - timedelta(days=2),
#     datetime.now(),
#     blacklisted_tokens=set(),
#     offset=0,
#     limit=100,
# )
# flipside.query(query)
