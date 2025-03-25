import warnings

warnings.filterwarnings("ignore", message=".*pydantic.error_wrappers:ValidationError.*", category=UserWarning)

from flipside import Flipside

from .common import flipside_queries
from .common.logger import logger
from .config import BLACKLISTED_TOKENS


class FlipsideClientException(Exception):
    pass


def fetch_data_for_period(
    start_time,
    end_time,
    flipside_apikey,
):
    offset = 0
    limit = 100000
    all_swaps = []
    stop = False
    while not stop:
        logger.debug(f"Собираем данные за {start_time} - {end_time} | offset: {offset}")
        swaps, count = get_swaps(
            flipside_apikey,
            start_time,
            end_time,
            offset=offset,
            limit=limit,
        )

        all_swaps.extend(swaps)
        if count < limit:
            stop = True
        else:
            offset += limit

    return all_swaps


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
    query = flipside_queries.sql_get_swaps(
        start_time,
        end_time,
        blacklisted_tokens=BLACKLISTED_TOKENS,
        offset=offset,
        limit=limit,
    )

    query_result_set = flipside.query(query)
    swaps = query_result_set.records if query_result_set.records else []
    count = len(query_result_set.records) if query_result_set.records else 0
    logger.info(
        f"Кол-во записей: {count} | Время запроса: {query_result_set.run_stats.query_exec_seconds}, {query_result_set.run_stats.elapsed_seconds}"
    )
    return swaps, count
