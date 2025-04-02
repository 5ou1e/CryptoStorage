import datetime

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
