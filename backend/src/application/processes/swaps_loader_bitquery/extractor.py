import json
import logging
import warnings
from datetime import datetime, timedelta

import requests

warnings.filterwarnings(
    "ignore",
    message=".*pydantic.error_wrappers:ValidationError.*",
    category=UserWarning,
)
from src.application.processes.swaps_loader_bitquery.common.bitquery_queries import get_dex_trades


logger = logging.getLogger(__name__)


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
    api_key,
    start_time,
    end_time,
    offset=0,
    limit=None,
):
    url = "https://streaming.bitquery.io/eap"

    query = get_dex_trades(
        start_time,
        end_time,
        offset,
        limit,
    )

    payload = json.dumps({
        "query": query,
        "variables": "{}"
    })

    headers = {
        "Content-Type": 'application/json',
        "Authorization": f"Bearer {api_key}"
    }

    print(payload)
    response = requests.post(url, headers=headers, data=payload)
    # print(response.text)
    data = response.json()

    trades = data["data"]["Solana"]["DEXTrades"]

    return trades, len(trades)

#
# trades, count = get_swaps(
#     "ory_at_bED3JXhq3eNCC-jPf_YbWXtjtgCK1FtrBsTCf08tRJw.tK1PWBeVVFYa_YL5k7ZhG2q3lEt5VjCGeGmrXOsB6jc",
#     datetime.now() - timedelta(minutes=1000),
#     datetime.now(),
#     limit=100000,
# )
# print(count)
