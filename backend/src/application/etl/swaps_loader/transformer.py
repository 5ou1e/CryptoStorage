from collections import defaultdict
from datetime import datetime, timezone
from decimal import Decimal
from typing import List, Tuple

from src.domain.constants import OKX_WALLET_ADDRESS, SOL_ADDRESS
from src.domain.entities.swap import Swap, SwapEventType
from src.domain.entities.token import Token
from src.domain.entities.wallet import (
    Wallet,
    WalletStatistic7d,
    WalletStatistic30d,
    WalletStatisticAll,
    WalletToken,
)
from uuid6 import uuid7

from .common import calculations


def transform_data(swaps, sol_prices):
    populate_swaps_data(swaps)
    wallets, tokens, activities, wallet_tokens = builds_objects(swaps, sol_prices)
    calculations.calculate_wallet_tokens(wallet_tokens, activities)
    return wallets, tokens, activities, wallet_tokens


def populate_swaps_data(swaps: list):
    """Дополняет данные свапов дополнительной информацией"""
    swaps_map = defaultdict(list)
    for swap in swaps:
        tx_id = swap["tx_id"]
        swaps_map[tx_id].append(swap)

    for tx_id, _swaps in swaps_map.items():
        swappers = defaultdict(lambda: defaultdict(list))
        swaps_count = len(_swaps)
        for swap in _swaps:
            token = (
                swap["swap_from_mint"]
                if swap["swap_to_mint"] == SOL_ADDRESS
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
                if OKX_WALLET_ADDRESS in swappers_list:
                    real_swapper = (
                        swappers_list[0]
                        if swappers_list[1] == OKX_WALLET_ADDRESS
                        else swappers_list[1]
                    )
                    for swap in _swaps:
                        swap["swapper"] = real_swapper
            elif swappers_count >= 3:
                for swap in _swaps:
                    swap["is_part_of_transaction_with_mt_3_swappers"] = True


def builds_objects(
    swaps: list,
    sol_prices: dict,
) -> Tuple[List[Wallet], List[Token], List[Swap], List[WalletToken]]:
    """Извлечение и создание обьектов кошельков, токенов и активностей из полученных swaps"""
    activities_list = []
    wallets = {}
    tokens = {}
    wallet_tokens = {}

    created_at = datetime.now(timezone.utc)

    for swap in swaps:

        if not all([swap["swapper"], swap["tx_id"]]):
            continue

        wallet_address = swap["swapper"]

        is_buy_swap = swap["swap_from_mint"] == SOL_ADDRESS
        token_address = swap["swap_to_mint"] if is_buy_swap else swap["swap_from_mint"]
        event_type = SwapEventType.BUY if is_buy_swap else SwapEventType.SELL
        quote_amount = (
            Decimal(str(swap["swap_from_amount"]))
            if is_buy_swap
            else Decimal(str(swap["swap_to_amount"]))
        )
        token_amount = (
            Decimal(str(swap["swap_to_amount"]))
            if is_buy_swap
            else Decimal(str(swap["swap_from_amount"]))
        )

        iso_string = swap["block_timestamp"].replace("Z", "+00:00")

        swap_timestamp = datetime.fromisoformat(iso_string)
        swap_minute = swap_timestamp.replace(second=0, microsecond=0)

        price_usd = Decimal(sol_prices[swap_minute])

        wallet = wallets.get(wallet_address)

        if not wallet:
            wallet = Wallet(
                id=uuid7(),  # fake temp id
                address=wallet_address,
                created_at=created_at,
                updated_at=created_at,
            )
            build_wallet_relations(wallet, created_at)
            wallets[wallet_address] = wallet
        wallet.last_activity_timestamp = max(
            swap_timestamp, wallet.last_activity_timestamp or swap_timestamp
        )
        wallet.first_activity_timestamp = min(
            swap_timestamp, wallet.first_activity_timestamp or swap_timestamp
        )

        token = tokens.get(token_address)
        if not token:
            token = Token(
                id=uuid7(),  # fake temp id
                address=token_address,
                is_metadata_parsed=False,
                created_at=created_at,
                updated_at=created_at,
            )
            tokens[token_address] = token

        activity = Swap(
            id=uuid7(),
            wallet_id=wallet.id,
            token_id=token.id,
            created_at=created_at,
            updated_at=created_at,
            tx_hash=swap["tx_id"],
            block_id=swap["block_id"],
            timestamp=swap_timestamp,
            event_type=event_type,
            quote_amount=quote_amount,
            token_amount=token_amount,
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
        activity.wallet_address = (
            wallet_address  # Для идентификации ибо ID из БД еще нету
        )
        activity.token_address = (
            token_address  # Для идентификации ибо ID из БД еще нету
        )
        activities_list.append(activity)

        if (wallet_address, token_address) not in wallet_tokens:
            wallet_token = WalletToken(
                id=uuid7(),
                wallet_id=wallet.id,
                token_id=token.id,
                created_at=created_at,
                updated_at=created_at,
            )
            wallet_token.wallet_address = (
                wallet_address  # Для идентификации ибо ID из БД еще нету
            )
            wallet_token.token_address = (
                token_address  # Для идентификации ибо ID из БД еще нету
            )
            wallet_tokens[(wallet_address, token_address)] = wallet_token

    wallets_list = [wallet for wallet in wallets.values()]
    tokens_list = [token for token in tokens.values()]
    wallet_tokens_list = [wt for wt in wallet_tokens.values()]

    return wallets_list, tokens_list, activities_list, wallet_tokens_list


def build_wallet_relations(wallet, created_at):
    wallet.stats_7d = WalletStatistic7d(
        wallet_id=wallet.id,
        created_at=created_at,
        updated_at=created_at,
    )
    wallet.stats_30d = WalletStatistic30d(
        wallet_id=wallet.id,
        created_at=created_at,
        updated_at=created_at,
    )
    wallet.stats_all = WalletStatisticAll(
        wallet_id=wallet.id,
        created_at=created_at,
        updated_at=created_at,
    )
