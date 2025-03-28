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
    blacklisted_tokens.add(
        SOL_ADDRESS
    )  # Добавляем SOL_ADDRESS чтобы исключить свапы WSOL -> WSOL
    blacklist_tokens_values = ",".join(f"'{token}'" for token in blacklisted_tokens)
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
                AND js.tx_id IS NULL -- Исключаем те tx_id, которые есть в Jupiter
        )
        SELECT *
        FROM (
            SELECT * FROM jupiter_swaps
            UNION ALL
            SELECT * FROM ez_swaps
        ) AS combined
        WHERE 
          (
            (SWAP_FROM_MINT = '{SOL_ADDRESS}' AND SWAP_TO_MINT NOT IN ({blacklist_tokens_values}))
            OR
            (SWAP_TO_MINT = '{SOL_ADDRESS}' AND SWAP_FROM_MINT NOT IN ({blacklist_tokens_values}))
          )
        ORDER BY row_id ASC
        LIMIT {limit} OFFSET {offset};
    """
    return query
