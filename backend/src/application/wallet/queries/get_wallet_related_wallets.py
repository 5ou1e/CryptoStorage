import asyncio
from collections import Counter, defaultdict

from src.application.common.utils import (
    classify_block_relation,
    classify_related_wallet_status,
    classify_token_trade_status,
)
from src.application.interfaces.repositories.swap import BaseSwapRepository
from src.application.interfaces.repositories.wallet import BaseWalletRepository, BaseWalletTokenRepository
from src.application.wallet.dto import CopiedByWalletDTO, CopyingWalletDTO, SimilarWalletDTO, WalletRelatedWalletsDTO
from src.application.wallet.dto.wallet_related_wallet import UndeterminedRelatedWalletDTO
from src.application.wallet.exceptions import WalletNotFoundException
from src.domain.entities.swap import SwapEventType


class GetWalletRelatedWalletsHandler:
    def __init__(
        self,
        wallet_repository: BaseWalletRepository,
        wallet_token_repository: BaseWalletTokenRepository,
        swap_repository: BaseSwapRepository,
    ) -> None:
        self._wallet_repository = wallet_repository
        self._wallet_token_repository = wallet_token_repository
        self._swap_repository = swap_repository

    async def __call__(self, address: str) -> WalletRelatedWalletsDTO:
        wallet = await self._wallet_repository.get_by_address(address=address)
        if not wallet:
            raise WalletNotFoundException(address)
        wallet_id = str(wallet.id)

        async def t(token_id, sem):
            async with sem:
                (
                    first_buy_activity,
                    first_sell_activity,
                ) = await asyncio.gather(
                    self._swap_repository.get_first_by_wallet_and_token(
                        wallet_id,
                        token_id,
                        event_type=SwapEventType.BUY,
                    ),
                    self._swap_repository.get_first_by_wallet_and_token(
                        wallet_id,
                        token_id,
                        event_type=SwapEventType.SELL,
                    ),
                )
                if not first_buy_activity or not (first_buy_block_id := first_buy_activity.block_id):
                    return
                if not first_sell_activity or not (first_sell_block_id := first_sell_activity.block_id):
                    return
                # print(first_sell_activity)
                # print(first_buy_activity)

                neighbor_buy_activities = await self._swap_repository.get_neighbors_by_token(
                    token_id=token_id,
                    block_id=first_buy_block_id,
                    event_type="buy",
                    exclude_wallets=[wallet_id],
                )
                # print(neighbor_buy_activities)
                neighbor_sell_activities = await self._swap_repository.get_neighbors_by_token(
                    token_id=token_id,
                    block_id=first_sell_block_id,
                    event_type="sell",
                    exclude_wallets=[wallet_id],
                )
                # print(neighbor_sell_activities)

                # Маппинг по кошелькам, с первыми покупками\продажами
                wallets_map = defaultdict(
                    lambda: {
                        "buy": None,
                        "sell": None,
                    }
                )
                for activity in neighbor_buy_activities:
                    if not hasattr(activity, "block_id"):
                        print(activity.__dict__)
                    current_buy = wallets_map[activity.wallet_id]["buy"]
                    if current_buy is None or activity.block_id < current_buy.block_id:
                        wallets_map[activity.wallet_id]["buy"] = activity
                for activity in neighbor_sell_activities:
                    current_sell = wallets_map[activity.wallet_id]["sell"]
                    if current_sell is None or activity.block_id < current_sell.block_id:
                        wallets_map[activity.wallet_id]["sell"] = activity

                for (
                    w_id_,
                    wallet_data,
                ) in wallets_map.items():
                    fb, fs = (
                        wallet_data["buy"],
                        wallet_data["sell"],
                    )
                    if not (fb and fs):
                        continue
                    buy_status = classify_block_relation(
                        fb.block_id,
                        first_buy_block_id,
                    )
                    sell_status = classify_block_relation(
                        fs.block_id,
                        first_sell_block_id,
                    )
                    status = classify_token_trade_status(buy_status, sell_status)

                    related_wallets_map[w_id_][token_id] = {
                        "buy_status": buy_status,
                        "sell_status": sell_status,
                        "status": status,
                        "sell_timestamp": fs.timestamp,
                    }

        wallet_tokens = await self._wallet_token_repository.get_list(
            filter_by={
                "wallet_id": wallet_id,
                "total_buys_count__gt": 0,
                "total_sales_count__gt": 0,
            },
            order_by=["-last_activity_timestamp"],
            limit=3000,
        )

        related_wallets_map = defaultdict(dict)

        # Обрабатываем каждый токен асинхронно для ускорения
        sem = asyncio.Semaphore(10)
        await asyncio.gather(*(t(wallet_token.token_id, sem) for wallet_token in wallet_tokens))

        # print(dict(related_wallets_map))

        # Получаем необходимые кошельки из БД
        wallet_ids = [w_id for w_id, tokens in related_wallets_map.items() if len(tokens) >= 3]
        wallets = await self._wallet_repository.get_list(
            filter_by={
                "id__in": wallet_ids,
                "is_bot": False,
            },
            prefetch=["details", "stats_all", "stats_30d"],
        )

        response_map = {
            "copying": CopyingWalletDTO,
            "copied_by": CopiedByWalletDTO,
            "similar": SimilarWalletDTO,
            "undetermined": UndeterminedRelatedWalletDTO,
        }
        result = {
            "copying": [],
            "copied_by": [],
            "similar": [],
            "undetermined": [],
        }

        for wallet in wallets:
            total_token_count = wallet.stats_all.total_token if wallet.stats_all else 0
            if total_token_count and total_token_count >= 20000:
                continue

            tokens = related_wallets_map.get(wallet.id, {})
            status_counts = Counter()
            last_activity_timestamp = wallet.last_activity_timestamp
            last_intersected_tokens_trade_timestamp = None
            statuses = set()

            for token in tokens.values():
                status = token["status"]
                status_counts[status] += 1
                statuses.add(status)
                if token["sell_timestamp"]:
                    last_intersected_tokens_trade_timestamp = max(
                        last_intersected_tokens_trade_timestamp or token["sell_timestamp"],
                        token["sell_timestamp"],
                    )

            mixed_count = status_counts.get("mixed", 0)
            same_count = status_counts.get("same", 0)
            after_count = status_counts.get("after", 0)
            before_count = status_counts.get("before", 0)

            intersected_tokens_count = mixed_count + same_count + after_count + before_count
            intersected_tokens_percent = (
                round(intersected_tokens_count / total_token_count * 100, 2)
                if intersected_tokens_count and total_token_count
                else None
            )

            wallet_status, color = classify_related_wallet_status(
                statuses, intersected_tokens_count, total_token_count, before_count, after_count
            )

            total_profit_usd_30d = wallet.stats_30d.total_profit_usd
            total_profit_multiplier_30d = wallet.stats_30d.total_profit_multiplier
            response_class = response_map.get(wallet_status)
            if response_class:
                result[wallet_status].append(
                    response_class(
                        address=wallet.address,
                        last_activity_timestamp=last_activity_timestamp,
                        last_intersected_tokens_trade_timestamp=last_intersected_tokens_trade_timestamp,
                        total_profit_usd_30d=total_profit_usd_30d,
                        total_profit_multiplier_30d=total_profit_multiplier_30d,
                        total_token_count=total_token_count,
                        intersected_tokens_count=intersected_tokens_count,
                        intersected_tokens_percent=intersected_tokens_percent,
                        mixed_count=mixed_count,
                        same_count=same_count,
                        before_count=before_count,
                        after_count=after_count,
                        color=color,
                    )
                )
        # Сортируем по дате последнего трейда пересекающихся токенов
        copying = sorted(
            result["copying"],
            key=lambda x: x.last_intersected_tokens_trade_timestamp,
            reverse=True,
        )
        copied_by = sorted(
            result["copied_by"],
            key=lambda x: x.last_intersected_tokens_trade_timestamp,
            reverse=True,
        )
        similar = sorted(
            result["similar"],
            key=lambda x: x.last_intersected_tokens_trade_timestamp,
            reverse=True,
        )
        undetermined = sorted(
            result["undetermined"],
            key=lambda x: x.last_intersected_tokens_trade_timestamp,
            reverse=True,
        )
        return WalletRelatedWalletsDTO(
            copying_wallets=copying,
            copied_by_wallets=copied_by,
            similar_wallets=similar,
            undetermined_wallets=undetermined,
        )
