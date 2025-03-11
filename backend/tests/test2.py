import asyncio
import logging

from sqlalchemy import (
    MetaData,
)

from src.infra.db.models.sqlalchemy.wallet import Wallet

# Устанавливаем уровень логирования
logger = logging.getLogger("sqlalchemy.engine")
logger.setLevel(logging.DEBUG)

# Вывод логов в консоль
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
logger.addHandler(console_handler)


async def test_core():
    metadata = MetaData()
    from src.infra.db.setup import AsyncSessionLocal

    # Получаем сессию через контекстный менеджер
    async with AsyncSessionLocal() as session:
        new_wallet = Wallet(address="My Wallet")
        # Добавляем объект в сессию
        session.add(new_wallet)
        # Коммитим транзакцию
        await session.commit()


async def main():
    await test_core()


if __name__ == "__main__":
    asyncio.run(main())
