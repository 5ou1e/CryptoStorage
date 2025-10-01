import json
import logging
import warnings
from collections import defaultdict
from datetime import datetime, timedelta

import requests

warnings.filterwarnings(
    "ignore",
    message=".*pydantic.error_wrappers:ValidationError.*",
    category=UserWarning,
)
from src.application.processes.swaps_loader_bitquery.common.bitquery_queries import get_dex_trades


logger = logging.getLogger(__name__)


class BitqueryError(Exception):
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

    try:
        response = requests.post(url, headers=headers, data=payload)

        print(response.text[:500])
        response.raise_for_status()

        data = response.json()
        trades = data["data"]["Solana"]["DEXTrades"]

    except Exception as e:
        raise BitqueryError(e)

    return trades, len(trades)


# trades, count = get_swaps(
#     "ory_at_bED3JXhq3eNCC-jPf_YbWXtjtgCK1FtrBsTCf08tRJw.tK1PWBeVVFYa_YL5k7ZhG2q3lEt5VjCGeGmrXOsB6jc",
#     datetime.now() - timedelta(minutes=1000),
#     datetime.now(),
#     limit=1,
# )
#
# mapped_swaps = defaultdict(list)
#
# for swap in trades:
#     mapped_swaps[swap["Transaction"]["Signature"]].append(swap)
#
# # В случае если есть свап Jupiter (Общий) внутри свапов одной транзакции, берем только его
# all_swaps = []
# for tx_id, swaps in mapped_swaps.items():
#     is_jup = False
#
#     for swap in swaps:
#         if swap["Instruction"]["Program"]["Name"] == "jupiter":
#             is_jup = True
#             all_swaps.append(swap)
#
#     if not is_jup:
#         all_swaps.extend(swaps)
#
# print(len(trades))
# print(len(all_swaps))
# print(all_swaps)
#
#
# converted_swaps = []
# for swap in trades:
#     conv = {}
#     # print(json.dumps(swap, indent=3))
#     conv["tx_id"] = swap["Transaction"]["Signature"]
#     conv["block_id"] = int(swap["Block"]["Slot"])
#     conv["block_timestamp"] = swap["Block"]["Time"]
#
#     conv["swapper"] = swap["Transaction"]["Signer"]
#     conv["swap_from_mint"] = swap["Trade"]["Sell"]["Currency"]["MintAddress"]
#     conv["swap_from_amount"] = swap["Trade"]["Sell"]["Amount"]
#     conv["swap_to_mint"] = swap["Trade"]["Buy"]["Currency"]["MintAddress"]
#     conv["swap_to_amount"] = swap["Trade"]["Buy"]["Amount"]
#
#     converted_swaps.append(conv)
#
# swaps = converted_swaps
#
#
#
# for swap in all_swaps:
#     print(json.dumps(swap, indent=3))
# print(count)
