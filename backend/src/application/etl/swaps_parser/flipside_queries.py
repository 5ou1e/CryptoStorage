import datetime

from flipside import Flipside

from .config import SOL_ADDRESS
from .logger import logger


def sql_get_swaps(
    start_time: datetime,
    end_time: datetime,
    offset: int = 0,
    limit: int | None = None,
):
    """SQL-запрос для получения swaps с Flipside-crypto"""
    if limit is None:
        limit = 100000
    sql = f"""
    SELECT
      tx_id,
      block_id,
      swapper,
      swap_from_mint,
      swap_to_mint,
      swap_from_amount,
      swap_to_amount,
      BLOCK_TIMESTAMP,
    FROM
      solana.defi.ez_dex_swaps
    WHERE
      BLOCK_TIMESTAMP >= '{start_time}'
      AND BLOCK_TIMESTAMP < '{end_time}'
      AND (
        SWAP_FROM_MINT = '{SOL_ADDRESS}'
        OR SWAP_TO_MINT = '{SOL_ADDRESS}'
      )
    ORDER BY EZ_SWAPS_ID ASC
      LIMIT {limit} OFFSET {offset}
    """
    return sql


def sql_get_swaps_jupiter(
    start_time: datetime,
    end_time: datetime,
    offset: int = 0,
    limit: int | None = None,
):
    """SQL-запрос для получения Jupiter-swaps с Flipside-crypto"""
    if limit is None:
        limit = 100000
    sql = f"""
    SELECT
      tx_id,
      block_id,
      swapper,
      swap_from_mint,
      swap_to_mint,
      swap_from_amount,
      swap_to_amount,
      BLOCK_TIMESTAMP,
    FROM
      solana.defi.fact_swaps_jupiter_summary
    WHERE
      BLOCK_TIMESTAMP >= '{start_time}'
      AND BLOCK_TIMESTAMP < '{end_time}'
      AND (
        SWAP_FROM_MINT = '{SOL_ADDRESS}'
        OR SWAP_TO_MINT = '{SOL_ADDRESS}'
      )
    ORDER BY FACT_SWAPS_JUPITER_SUMMARY_ID ASC
      LIMIT {limit} OFFSET {offset}
    """
    return sql


def get_swaps(
    flipside_apikey,
    start_time,
    end_time,
    offset=0,
    limit=None,
):
    flipside = Flipside(
        flipside_apikey,
        "https://api-v2.flipsidecrypto.xyz",
    )
    _query = sql_get_swaps(
        start_time,
        end_time,
        offset=offset,
        limit=limit,
    )
    query_result_set = flipside.query(_query)
    swaps = query_result_set.records if query_result_set.records else []
    records_count = len(query_result_set.records) if query_result_set.records else 0
    logger.debug(
        f"Кол-во записей: {records_count} | Время запроса: {query_result_set.run_stats.query_exec_seconds}, {query_result_set.run_stats.elapsed_seconds}"
    )
    return swaps, records_count


def get_swaps_jupiter(
    flipside_apikey,
    start_time,
    end_time,
    offset=0,
    limit=None,
):
    flipside = Flipside(
        flipside_apikey,
        "https://api-v2.flipsidecrypto.xyz",
    )
    _query = sql_get_swaps_jupiter(
        start_time,
        end_time,
        offset=offset,
        limit=limit,
    )
    query_result_set = flipside.query(_query)
    swaps = query_result_set.records if query_result_set.records else []
    records_count = len(query_result_set.records) if query_result_set.records else 0
    logger.debug(
        f"Кол-во записей Юпитер: {records_count} | Время запроса: {query_result_set.run_stats.query_exec_seconds}, {query_result_set.run_stats.elapsed_seconds}"
    )
    return swaps, records_count
