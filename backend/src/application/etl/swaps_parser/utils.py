import uuid
from collections import defaultdict
from datetime import datetime
from decimal import Decimal
from typing import List, Tuple

from src.infra.db.models.tortoise import (
    Swap,
    Token,
    Wallet,
    WalletDetail,
    WalletStatistic7d,
    WalletStatistic30d,
    WalletStatisticAll,
)

from .config import SOL_ADDRESS
from .logger import logger


def populate_swaps_data(mapped_swaps: dict):
    """Дополняет данные свапов дополнительной информацией"""
    okx_wallet = "HV1KXxWFaSeriyFvXyx48FqG9BoFbfinB8njCJonqP7K"
    for tx_id, _swaps in mapped_swaps.items():
        swappers = defaultdict(lambda: defaultdict(list))
        swaps_count = len(_swaps)
        for swap in _swaps:
            token = (
                swap["swap_from_mint"]
                if swap["swap_to_mint"] == "So11111111111111111111111111111111111111112"
                else swap["swap_to_mint"]
            )
            event_type = "buy" if swap["swap_to_mint"] == token else "sell"
            swappers[swap["swapper"]][token].append(event_type)
        swappers_list = [swapper for swapper in swappers.keys()]
        swappers_count = len(swappers_list)
        if swaps_count >= 2:
            if swappers_count == 1:
                for swap in _swaps:
                    for token, events in swappers[swap["swapper"]].items():
                        if len(events) >= 2 and ("buy" in events and "sell" in events):
                            swap["is_part_of_arbitrage_swap_event"] = True
            elif swappers_count == 2:
                if okx_wallet in swappers_list:
                    real_swapper = swappers_list[0] if swappers_list[1] == okx_wallet else swappers_list[1]
                    for swap in _swaps:
                        swap["swapper"] = real_swapper
            elif swappers_count >= 3:
                for swap in _swaps:
                    swap["is_part_of_transaction_with_mt_3_swappers"] = True


def combine_swaps(swaps: list[dict], swaps_jupiter: list[dict]):
    """Обьединяет свапы с двух источников"""
    mapped_swaps_jupiter = defaultdict(list)
    for swap in swaps_jupiter:
        if (
            not swap["swapper"] == None
        ):  # Бывает что swapper - None , тогда не записываем свап как Jupiter-Swap, чтобы учитывался свап из другой таблицы
            mapped_swaps_jupiter[swap["tx_id"]].append(swap)

    mapped_swaps_all = defaultdict(list)
    for swap in swaps:
        tx_id = swap["tx_id"]
        if tx_id not in mapped_swaps_jupiter:
            mapped_swaps_all[tx_id].append(swap)

    mapped_swaps = mapped_swaps_all | mapped_swaps_jupiter

    populate_swaps_data(mapped_swaps)
    combined_swaps = [swap for _swaps in mapped_swaps.values() for swap in _swaps]

    logger.debug(
        f"\nСвапов - Всего: {len(swaps)} | Юпитер: {len(swaps_jupiter)}"
        f"\nТранзакций - Всего: {len(mapped_swaps)} | Без юпитера: {len(mapped_swaps_all)} | Юпитер: {len(mapped_swaps_jupiter)}"
        f"\nСвапов суммарно: {len(combined_swaps)}"
    )

    return combined_swaps


def filter_swaps(
    swaps: list,
    blacklisted_tokens: List[str] | None = None,
) -> list[dict]:
    """Отфильтровывает неподходящие активности"""
    blacklisted_tokens = blacklisted_tokens or []

    def _filter(swap):
        swap_from_mint = swap.get("swap_from_mint")
        swap_to_mint = swap.get("swap_to_mint")
        if not (swap_from_mint == SOL_ADDRESS or swap_to_mint == SOL_ADDRESS):
            return False
        elif swap_from_mint == SOL_ADDRESS:
            if swap_to_mint in blacklisted_tokens:
                return False
        elif swap_to_mint == SOL_ADDRESS:
            if swap_from_mint in blacklisted_tokens:
                return False
        return True

    filtered_swaps = list(filter(_filter, swaps))
    return filtered_swaps


def extract_and_build_objects(
    swaps: list,
    sol_prices: dict,
) -> Tuple[List[Wallet], List[Token], List[Swap]]:
    """Извлечение и создание обьектов кошельков, токенов и активностей из полученных swaps"""
    activities = []
    wallets = []
    tokens = []
    unique_wallet_addresses = set()
    unique_token_addresses = set()

    for swap in swaps:
        if not all([swap["swapper"], swap["tx_id"]]):
            continue

        wallet_address = swap["swapper"]
        if swap["swap_from_mint"] == SOL_ADDRESS:
            token_address = swap["swap_to_mint"]
            event_type = "buy"
            quote_amount = Decimal(str(swap["swap_from_amount"]))
            token_amount = Decimal(str(swap["swap_to_amount"]))
        else:
            token_address = swap["swap_from_mint"]
            event_type = "sell"
            quote_amount = Decimal(str(swap["swap_to_amount"]))
            token_amount = Decimal(str(swap["swap_from_amount"]))

        iso_string = swap["block_timestamp"]
        iso_string = iso_string.replace("Z", "+00:00")

        swap_datetime = datetime.fromisoformat(iso_string)
        swap_minute = swap_datetime.replace(second=0, microsecond=0)

        sol_price = sol_prices[swap_minute]
        cost_usd = Decimal(str(quote_amount * sol_price))
        price_usd = Decimal(str(cost_usd / token_amount)) if token_amount else None

        activity = Swap(
            id=uuid.uuid1(),
            tx_hash=swap["tx_id"],
            block_id=swap["block_id"],
            timestamp=swap_datetime.timestamp(),
            event_type=event_type,
            quote_amount=quote_amount,
            token_amount=token_amount,
            cost_usd=cost_usd,
            price_usd=price_usd,
            is_part_of_transaction_with_mt_3_swappers=swap.get(
                "is_part_of_transaction_with_mt_3_swappers",
                False,
            ),
            is_part_of_arbitrage_swap_event=swap.get(
                "is_part_of_arbitrage_swap_event",
                False,
            ),
        )
        activity.wallet_address = wallet_address
        activity.token_address = token_address
        activities.append(activity)

        if wallet_address not in unique_wallet_addresses:
            unique_wallet_addresses.add(wallet_address)
            wallet = Wallet(address=wallet_address)
            wallets.append(wallet)
        if token_address not in unique_token_addresses:
            unique_token_addresses.add(token_address)
            token = Token(
                address=token_address,
            )
            tokens.append(token)
    return wallets, tokens, activities


def split_time_range(start_time, end_time, parts):
    """Разбивает временной промежуток на равные части"""
    delta = (end_time - start_time) / parts
    intervals = [
        (
            start_time + i * delta,
            start_time + (i + 1) * delta,
        )
        for i in range(parts - 1)
    ]
    # Добавляем последний интервал, чтобы гарантировать точное совпадение с end_time
    intervals.append(
        (
            start_time + (parts - 1) * delta,
            end_time,
        )
    )
    return intervals


def create_wallets_relations(wallets):
    wallet_details = []
    wallet_stats_7d = []
    wallet_stats_30d = []
    wallet_stats_all = []

    for wallet in wallets:
        _wallet_details = WalletDetail(
            wallet_id=wallet.id,
        )
        wallet_details.append(_wallet_details)
        _wallet_stats_7d = WalletStatistic7d(
            wallet_id=wallet.id,
        )
        wallet_stats_7d.append(_wallet_stats_7d)
        _wallet_stats_30d = WalletStatistic30d(
            wallet_id=wallet.id,
        )
        wallet_stats_30d.append(_wallet_stats_30d)
        _wallet_stats_all = WalletStatisticAll(
            wallet_id=wallet.id,
        )
        wallet_stats_all.append(_wallet_stats_all)

    return (
        wallet_details,
        wallet_stats_7d,
        wallet_stats_30d,
        wallet_stats_all,
    )
