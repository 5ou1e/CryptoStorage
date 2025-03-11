import asyncio
import logging

import aiohttp
from tortoise import Tortoise

from src.infra.db.models.tortoise import (
    TgSentWallet,
    Wallet,
)
from src.infra.db.setup_tortoise import (
    init_db_async,
)
from src.settings import config

logger = logging.getLogger("tasks.send_wallets_in_tg")


async def send_wallets_in_tg_async():
    try:
        await init_db_async()
        await process()
    finally:
        await Tortoise.close_connections()


async def process():
    # Выбираем кошельки, которых нет в таблице SentWallet
    wallets = await get_wallets_to_send()
    logger.info(f"Всего кошельков подходящих под фильтры: {len(wallets)}")
    if wallets:
        await send_wallets_in_batches(wallets, batch_size=20)


async def get_wallets_to_send():
    return (
        await Wallet.filter(
            stats_all__winrate__gte=30,
            stats_all__total_profit_usd__gte=5000,
            stats_all__total_profit_multiplier__gte=40,
            stats_all__total_token__gte=4,
            stats_all__token_avg_buy_amount__gte=200,
            stats_all__token_avg_buy_amount__lte=1000,
            stats_all__token_buy_sell_duration_median__gte=60,
            stats_7d__total_token__gte=1,
            details__is_scammer=False,
            details__is_bot=False,
            tg_sent__isnull=True,
        )
        .prefetch_related(
            "stats_all",
        )
        .all()
    )


async def send_wallets_in_batches(wallets, batch_size=50):
    # Разбиваем список кошельков на части по batch_size
    for i in range(0, len(wallets), batch_size):
        batch = wallets[i : i + batch_size]
        try:
            await send_tg_message(batch)
            # Можно добавить логику для сохранения отправленных кошельков в базе данных, если нужно
            await TgSentWallet.bulk_create([TgSentWallet(wallet_id=w.id) for w in batch])
        except Exception as e:
            logger.error(f"Ошибка при отправке уведомления в тг для пакета {i // batch_size + 1}: {e}")
        await asyncio.sleep(5)


async def send_tg_message(wallets):
    def format_wallet(w, number):
        winrate = f"{w.stats_all.winrate:.2f}%" if w.stats_all and w.stats_all.winrate else "N/A"
        profit = f"{w.stats_all.total_profit_usd:.2f}$" if w.stats_all and w.stats_all.total_profit_usd else "N/A"
        formatted = (
            f"<b>{number}.</b> <b><code>{w.address}</code></b>"
            f"  <a href='https://cryptostorage.space/ru/solana/wallet/{w.address}/statistics/'>🔗</a>"
            f"\n└  В/Р: <b>{winrate}</b>"
            f"     Профит: <b>{profit}</b>"
        )
        return formatted

    if not wallets:
        return
    url = f"https://api.telegram.org/bot{config.telegram.bot_token}/sendMessage"
    message = "🚀 Подборка новых кошельков!\n\n"
    message += "\n\n".join([format_wallet(w, number + 1) for number, w in enumerate(wallets)])

    async with aiohttp.ClientSession() as session:
        async with session.post(
            url,
            json={
                "chat_id": config.telegram.wallet_alerts_channel_id,
                "text": message,
                "parse_mode": "HTML",
            },
        ) as response:
            response.raise_for_status()
