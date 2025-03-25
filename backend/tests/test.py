import asyncio
import logging
from datetime import datetime

from sqlalchemy import case, delete, func, select, text
from sqlalchemy.dialects.postgresql import insert

from src.infra.db.sqlalchemy.models import Swap
from src.infra.db.sqlalchemy.setup import AsyncSessionLocal, engine, get_db_session

# Создаем основной логгер
logger = logging.getLogger(__name__)

# Устанавливаем общий уровень логирования
logger.setLevel(logging.DEBUG)

# Формат для логов
log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Форматтер для логов
formatter = logging.Formatter(log_format, datefmt="%Y-%m-%d %H:%M:%S")

# Создаем обработчик для записи в файл
file_handler = logging.FileHandler("swaps_parser.log", encoding="utf-8")
file_handler.setLevel(logging.INFO)  # Уровень логирования для файла
file_handler.setFormatter(formatter)

# Создаем обработчик для вывода в консоль
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)  # Уровень логирования для консоли
console_handler.setFormatter(formatter)

# Добавляем обработчики в логгер
logger.addHandler(file_handler)
logger.addHandler(console_handler)


async def main():
    BATCH_SIZE = 1  # размер одной пачки
    count = 0
    async with AsyncSessionLocal() as session:
        while True:
            result = await session.execute(
                delete(Swap)
                .where(Swap.token_id == "01959d63-0c2f-720a-b45b-d9472ee3045a")
                .limit(BATCH_SIZE)  # Удаляем ограниченное количество записей
            )

            if result.rowcount == 0:
                break  # Если больше нечего удалять, выходим

            await session.commit()  # Фиксируем удаление
            count += 1
            logger.info(count)
            break
        print("Удаление завершено.")


asyncio.run(main())
