from datetime import datetime, timezone

import pytz

from src.infra.db.models.tortoise import (
    WalletToken,
)

from .logger import logger


def calculate_token_stats(
    token_data: dict,
) -> None:
    """Пересчитывает статистику для связки кошелька с токеном"""
    stats = token_data["stats"]
    token_activities = token_data["activities"]

    for activity in token_activities:
        if activity.event_type == "buy":
            stats.total_buys_count += 1
            stats.total_buy_amount_usd += activity.cost_usd if activity.cost_usd else 0
            stats.total_buy_amount_token += activity.token_amount if activity.token_amount else 0
            if not stats.first_buy_timestamp or (activity.timestamp <= stats.first_buy_timestamp):
                stats.first_buy_timestamp = activity.timestamp
                stats.first_buy_price_usd = activity.price_usd
        else:
            stats.total_sales_count += 1
            stats.total_sell_amount_usd += activity.cost_usd if activity.cost_usd else 0
            stats.total_sell_amount_token += activity.token_amount if activity.token_amount else 0
            if not stats.first_sell_timestamp or (activity.timestamp <= stats.first_sell_timestamp):
                stats.first_sell_timestamp = activity.timestamp
                stats.first_sell_price_usd = activity.price_usd

        if not stats.last_activity_timestamp or (activity.timestamp >= stats.last_activity_timestamp):
            stats.last_activity_timestamp = activity.timestamp

        if activity.is_part_of_transaction_with_mt_3_swappers:
            stats.total_swaps_from_txs_with_mt_3_swappers += 1
        if activity.is_part_of_arbitrage_swap_event:
            stats.total_swaps_from_arbitrage_swap_events += 1

    if (
        stats.first_buy_timestamp
        and stats.first_sell_timestamp
        and (stats.first_buy_timestamp <= stats.first_sell_timestamp)
    ):
        stats.first_buy_sell_duration = stats.first_sell_timestamp - stats.first_buy_timestamp
    if stats.total_buys_count > 0:
        stats.total_profit_usd = stats.total_sell_amount_usd - stats.total_buy_amount_usd
        stats.total_profit_percent = (
            round(
                stats.total_profit_usd / stats.total_buy_amount_usd * 100,
                2,
            )
            if not stats.total_buy_amount_usd == 0
            else None
        )

    stats.updated_at = datetime.now(pytz.timezone("Europe/Moscow"))


def recalculate_wallet_token_stats(wallets_dict):
    new_count = 0
    for wallet_data in wallets_dict.values():
        wallet = wallet_data["wallet"]
        tokens = wallet_data["tokens"]
        for token_data in tokens.values():
            token = token_data["token"]
            stats = token_data["stats"]
            # Создаем новый обьект токен-статистики если его не существует для токена
            if not stats:
                new_count += 1
                stats = token_data["stats"] = WalletToken(
                    token_id=token.id,
                    wallet_id=wallet.id,
                )
            calculate_token_stats(token_data)
    logger.info(f"Новых токен-статс {new_count}")


def calculate_wallet_first_last_activity_timestamps(
    wallets: list,
    mapped_data: dict,
):
    for wallet in wallets:
        wallet_data = mapped_data[wallet.address]
        # Собираем все активности для кошелька
        all_activities = [
            activity for token_data in wallet_data["tokens"].values() for activity in token_data["activities"]
        ]
        last_activity_timestamp = (
            datetime.fromtimestamp(
                max(
                    all_activities,
                    key=lambda x: x.timestamp,
                ).timestamp,
                tz=timezone.utc,
            )
            if all_activities
            else None
        )
        last_activity_timestamp_in_db = wallet.last_activity_timestamp
        if last_activity_timestamp and (
            last_activity_timestamp_in_db is None or last_activity_timestamp > last_activity_timestamp_in_db
        ):
            wallet.last_activity_timestamp = last_activity_timestamp

        first_activity_timestamp = (
            datetime.fromtimestamp(
                min(
                    all_activities,
                    key=lambda x: x.timestamp,
                ).timestamp,
                tz=timezone.utc,
            )
            if all_activities
            else None
        )
        first_activity_timestamp_in_db = wallet.first_activity_timestamp
        if first_activity_timestamp and (
            first_activity_timestamp_in_db is None or first_activity_timestamp < first_activity_timestamp_in_db
        ):
            wallet.first_activity_timestamp = first_activity_timestamp

