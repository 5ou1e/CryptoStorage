import asyncio
import logging

import requests
from datetime import datetime, timedelta, timezone

from src.settings import config
from src.infra.db.sqlalchemy.repositories.flipside import (
    SQLAlchemyFlipsideConfigRepositoryInterface,
)
from src.infra.db.sqlalchemy.setup import AsyncSessionMaker

logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = config.telegram.bot_token
TELEGRAM_CHAT_ID = config.telegram.wallet_alerts_channel_id
CHECK_INTERVAL = 600  # как часто проверять, в секундах


def send_telegram_message(text: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": text})


async def get_swaps_loader_config():
    async with AsyncSessionMaker() as session:
        repo = SQLAlchemyFlipsideConfigRepositoryInterface(session)
        return await repo.get_first()


async def main():
    logger.info(f"Запущен процесс отслеживания задержек в сборе транзакций!")
    while True:
        config_row = await get_swaps_loader_config()
        db_time = config_row.swaps_parsed_until_block_timestamp

        now = datetime.now(timezone.utc)
        delta: timedelta = now - db_time

        if delta > timedelta(hours=3):
            # разница в часах и минутах
            hours, remainder = divmod(int(delta.total_seconds()), 3600)
            minutes, seconds = divmod(remainder, 60)

            send_telegram_message(
                f"🆘🆘🆘 Предупреждение!"
                f" Время последнего загруженного свапа: {db_time} "
                f"(отставание {hours}ч {minutes}м {seconds}с)"
            )

        await asyncio.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    asyncio.run(main())
