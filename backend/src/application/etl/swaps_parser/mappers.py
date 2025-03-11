from collections import defaultdict
from typing import List

from src.infra.db.models.tortoise import Swap, Token, Wallet


def map_data_by_wallets(
    wallets: List[Wallet],
    tokens: List[Token],
    activities: List[Swap],
) -> dict:
    """Маппинг данных по кошелькам"""

    # {
    #     wallet_id: {
    #         'wallet': wallet_object,  # Объект кошелька
    #         'tokens': {
    #             token_id: {
    #                 'token': token_object,  # Объект токена
    #                 'activities': [activity_1, activity_2, ...],  # Список активностей для этого токена
    #                 'stats': stats_object  # Статистика для токена (если есть)
    #             },
    #             ...
    #         },
    #     },
    #     ...
    # }
    def default_token_structure():
        return {
            "token": None,
            "activities": [],
            "stats": None,
        }  # Словарь с токеном и списком активностей

    def default_wallet_structure():
        return {
            "wallet": None,
            "tokens": defaultdict(default_token_structure),
        }

    mapped_data = defaultdict(default_wallet_structure)

    wallets_map = map_objects_by_address(wallets)
    tokens_map = map_objects_by_address(tokens)

    for activity in activities:
        wallet = wallets_map[activity.wallet_address]
        token = tokens_map[activity.token_address]
        activity.wallet_id = wallet.id
        activity.token_id = token.id
        mapped_data[wallet.address]["wallet"] = wallet
        mapped_data[wallet.address]["tokens"][token.address]["token"] = token
        mapped_data[wallet.address]["tokens"][token.address]["activities"].append(activity)

    return mapped_data


def update_mapped_data(mapped_data, created_wallets, created_tokens):
    # Обновляем маппинг с полученными ID
    wallets_map = map_objects_by_address(created_wallets)
    tokens_map = map_objects_by_address(created_tokens)

    for wallet_address, wallet_data in mapped_data.items():
        wallet = wallets_map[wallet_address]
        wallet_data["wallet"] = wallet

        for token_address, token_data in wallet_data["tokens"].items():
            token = tokens_map[token_address]
            token_data["token"] = token

            # Обновляем wallet_id и token_id у каждой активности
            for activity in token_data["activities"]:
                activity.wallet_id = wallet.id
                activity.token_id = token.id


def create_wallet_token_ids_list(
    activities: list[Swap],
):
    result = []
    unique_pairs = set()
    for activity in activities:
        pair = (
            activity.wallet_id,
            activity.token_id,
        )
        if pair not in unique_pairs:
            unique_pairs.add(pair)
            result.append(
                {
                    "wallet_id": activity.wallet_id,
                    "token_id": activity.token_id,
                }
            )
    return result


def map_objects_by_address(objects):
    mapped = {}
    for obj in objects:
        mapped[obj.address] = obj
    return mapped
