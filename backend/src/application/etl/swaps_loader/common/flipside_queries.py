import datetime
from pathlib import Path

from src.domain.constants import SOL_ADDRESS

BASE_DIR = Path(__file__).parent

with open(BASE_DIR / "tokens_blacklist.txt", "r") as file:
    BLACKLISTED_TOKENS = {line.strip() for line in file}


def sql_get_swaps(
    start_time: datetime,
    end_time: datetime,
    offset: int = 0,
    limit: int | None = None,
):
    """SQL-запрос для получения swaps с Flipside-crypto"""
    if limit is None:
        limit = 100000
    blacklist_tokens_values = ",".join(f"'{token}'" for token in BLACKLISTED_TOKENS)
    query = f"""
        WITH jupiter_swaps AS (
            SELECT
                tx_id,
                block_id,
                swapper,
                swap_from_mint,
                swap_to_mint,
                swap_from_amount,
                swap_to_amount,
                BLOCK_TIMESTAMP,
                FACT_SWAPS_JUPITER_SUMMARY_ID as row_id
            FROM
                solana.defi.fact_swaps_jupiter_summary
            WHERE
                  BLOCK_TIMESTAMP >= '{start_time}'
                  AND BLOCK_TIMESTAMP < '{end_time}'
                  AND (
                    SWAP_FROM_MINT = '{SOL_ADDRESS}'
                    OR SWAP_TO_MINT = '{SOL_ADDRESS}'
                  )
                AND swapper IS NOT NULL

        ),
        ez_swaps AS (
            SELECT
                ez.tx_id,
                ez.block_id,
                ez.swapper,
                ez.swap_from_mint,
                ez.swap_to_mint,
                ez.swap_from_amount,
                ez.swap_to_amount,
                ez.BLOCK_TIMESTAMP,
                ez.EZ_SWAPS_ID as row_id
            FROM
                solana.defi.ez_dex_swaps ez
            LEFT JOIN jupiter_swaps js ON ez.tx_id = js.tx_id
            WHERE
                  ez.BLOCK_TIMESTAMP >= '{start_time}'
                  AND ez.BLOCK_TIMESTAMP < '{end_time}'
                  AND (
                    ez.SWAP_FROM_MINT = '{SOL_ADDRESS}'
                    OR ez.SWAP_TO_MINT = '{SOL_ADDRESS}'
                  )
                AND js.tx_id IS NULL -- Исключаем те tx_id, которые есть в Jupiter
        )
        SELECT *
        FROM (
            SELECT * FROM jupiter_swaps
            UNION ALL
            SELECT * FROM ez_swaps
        ) AS combined
        WHERE NOT (
            (swap_from_mint = '{SOL_ADDRESS}' AND swap_to_mint IN ({blacklist_tokens_values}))
            OR
            (swap_to_mint = '{SOL_ADDRESS}' AND swap_from_mint IN ({blacklist_tokens_values}))
        )
        ORDER BY row_id ASC
        LIMIT {limit} OFFSET {offset};
    """
    return query
