from datetime import datetime, timezone
from typing import List, Tuple

from uuid6 import uuid7

from src.domain.entities.swap import Swap
from src.domain.entities.token import Token
from src.domain.entities.wallet import Wallet, WalletToken

from .common import calculations


def transform_data(swaps, sol_prices):
    wallets, tokens, activities, wallet_tokens = builds_objects(swaps, sol_prices)
    calculations.calculate_wallet_tokens(wallet_tokens, activities)
    return wallets, tokens, activities, wallet_tokens


def builds_objects(
    swaps: list,
    sol_prices: dict,
) -> Tuple[List[Wallet], List[Token], List[Swap], List[WalletToken]]:
    """Извлечение и создание обьектов кошельков, токенов и активностей из полученных swaps"""
    activities_list = swaps
    wallet_tokens = {}

    created_at = datetime.now(timezone.utc)

    for swap in activities_list:
        wallet_id = swap.wallet_id
        token_id = swap.token_id
        if (wallet_id, token_id) not in wallet_tokens:
            wallet_token = WalletToken(
                id=uuid7(),
                wallet_id=wallet_id,
                token_id=token_id,
                created_at=created_at,
                updated_at=created_at,
            )
            wallet_tokens[(wallet_id, token_id)] = wallet_token

    wallets_list = []
    tokens_list = []
    wallet_tokens_list = [wt for wt in wallet_tokens.values()]

    return wallets_list, tokens_list, activities_list, wallet_tokens_list
