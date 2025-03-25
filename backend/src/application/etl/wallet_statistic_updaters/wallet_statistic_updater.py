import asyncio
import logging
import random
from asyncio import Queue
from collections import defaultdict
from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.exc import DBAPIError
from tortoise import Tortoise
from tortoise.timezone import now

from src.application.etl.wallet_statistic_updaters import calculations
from src.domain.entities.wallet import (
    Wallet,
    WalletStatistic7d,
    WalletStatistic30d,
    WalletStatisticAll,
    WalletToken,
)
from src.infra.db.sqlalchemy.models import WalletToken as WalletTokenModel
from src.infra.db.sqlalchemy.repositories import (
    SQLAlchemyWalletRepository,
    SQLAlchemyWalletStatistic7dRepository,
    SQLAlchemyWalletStatistic30dRepository,
    SQLAlchemyWalletStatisticAllRepository,
    SQLAlchemyWalletTokenRepository,
)
from src.infra.db.sqlalchemy.setup import AsyncSessionLocal
from src.infra.db.tortoise.setup import init_db_async

logger = logging.getLogger("tasks.update_wallet_statistics")


async def update_single_wallet_statistics(
    wallet_id,
):
    raise NotImplementedError


async def receive_wallets_from_db(
    received_wallets_queue: Queue,
    count: int,
):
    """Загрузка данных из БД и помещение в очередь"""
    logger.info(f"Начинаем получение кошельков из БД")
    t1 = datetime.now()
    async with AsyncSessionLocal() as session:
        wallets: list[Wallet] = await SQLAlchemyWalletRepository(session).get_wallets_for_update_stats(count=count)
    t2 = datetime.now()
    logger.info(f"Получили {len(wallets)} кошельков из БД | Время: {t2 - t1}")
    for wallet in wallets:
        await received_wallets_queue.put(wallet)
    await received_wallets_queue.put(None)


async def fetch_wallets_related_data(
    received_wallets_queue: Queue,
    fetched_wallets_queue: Queue,
    batch_size: int,
    max_parallel: int = 1,
):
    """
    Асинхронно подгружает токены для кошельков, получаемых из очереди.

    Функция накапливает кошельки до достижения указанного размера батча (batch_size) и затем запускает
    параллельную обработку этих данных, ограничивая максимальное количество одновременно выполняемых задач
    параметром max_parallel. Обработанные данные отправляются в очередь fetched_wallets_queue.

    Параметры:
        received_wallets_queue (Queue): Очередь, из которой извлекаются объекты кошельков для обработки.
        fetched_wallets_queue (Queue): Очередь, в которую помещаются кошельки с подгруженными токенами.
        batch_size (int): Количество кошельков в батче для запуска параллельной обработки.
        max_parallel (int, optional): Максимальное количество параллельных задач. По умолчанию 1.
    """
    batch = []
    tasks = []  # Список активных задач обработки батчей
    while True:
        wallet: Wallet | None = await received_wallets_queue.get()
        if wallet is not None:
            batch.append(wallet)
        # Если набрали батч нужного размера или пришёл сигнал завершения (wallet is None)
        if (len(batch) >= batch_size) or (wallet is None and batch):
            # Создаём копию батча для передачи в задачу
            tasks.append(
                asyncio.create_task(
                    _fetch_related_data(
                        batch.copy(),
                        fetched_wallets_queue,
                    )
                )
            )
            batch.clear()
            # Если достигли лимита параллельных задач, ждём, пока хотя бы одна завершится
            if len(tasks) >= max_parallel:
                done, pending = await asyncio.wait(
                    tasks,
                    return_when=asyncio.FIRST_COMPLETED,
                )
                tasks = list(pending)  # Обновляем список, оставляя незавершённые задачи
        if wallet is None:
            # Ждём завершения всех оставшихся задач
            if tasks:
                await asyncio.gather(*tasks)
            await fetched_wallets_queue.put(None)
            logger.debug(f"Задача подгрузки токенов завершена")
            return


async def _fetch_related_data(
    wallets: list[Wallet],
    fetched_wallets_queue: Queue,
):
    # Загружаем токены для кошельков
    start = datetime.now()
    async with AsyncSessionLocal() as session:
        wallet_tokens = await SQLAlchemyWalletTokenRepository(session).get_wallet_tokens_by_wallets_list(
            [wallet.id for wallet in wallets]
        )
    end = datetime.now()
    wt_count = len(wallet_tokens)
    logger.debug(f"Подгрузили токены {len(wallets)} кошельков из БД | Токенов: {wt_count} | Время: {end-start}")
    start = datetime.now()

    wallet_tokens_map = defaultdict(list)
    for wt in wallet_tokens:
        wallet_tokens_map[wt.wallet_id].append(wt)

    for wallet in wallets:
        wallet.stats_7d = WalletStatistic7d(wallet_id=wallet.id)
        wallet.stats_30d = WalletStatistic30d(wallet_id=wallet.id)
        wallet.stats_all = WalletStatisticAll(wallet_id=wallet.id)
        wallet.tokens = [wt for wt in wallet_tokens_map[wallet.id]]

    end = datetime.now()
    logger.debug(f"Время создания обьектов токенов: {end-start}")
    for wallet in wallets:
        await fetched_wallets_queue.put(wallet)


async def calculate_wallets(
    received_wallets_queue: Queue,
    calculated_wallets_queue: Queue,
):
    """Обработка данных и передача в следующую очередь"""
    spent_time = timedelta(minutes=0)
    tokens_count = 0
    while True:
        wallet: Wallet | None = await received_wallets_queue.get()
        if wallet:
            #  TODO потестить как лучше с \ без await asyncio.sleep(0)
            # await asyncio.sleep(0)
            result = calculations.calculate_wallet_stats(wallet)
            tokens_count += len(wallet.tokens)

            await calculated_wallets_queue.put(wallet)
        else:
            await calculated_wallets_queue.put(None)
            logger.debug(f"Задача пересчета завершена")
            return tokens_count


async def update_wallets(
    calculated_wallets_queue: Queue,
    batch_size: int,
    max_parallel: int = 1,
) -> None:
    """Обновление обработанных данных в БД"""
    batch = []
    tasks = []  # Список активных задач обработки батчей
    while True:
        for t in tasks:
            if t.done():
                exception = t.exception()
                if exception:
                    # Обрабатываем ошибку внутри задачи
                    raise exception
        wallet: Wallet | None = await calculated_wallets_queue.get()
        if wallet is not None:
            batch.append(wallet)
        # Если набрали батч нужного размера или пришёл сигнал завершения (wallet is None)
        if (len(batch) >= batch_size) or (wallet is None and batch):
            # Создаём копию батча для передачи в задачу
            task = asyncio.create_task(_update_wallets_data(batch.copy()))
            tasks.append(task)
            batch.clear()

            # Если достигли лимита параллельных задач, ждём, пока хотя бы одна завершится
            if len(tasks) >= max_parallel:
                done, pending = await asyncio.wait(
                    tasks,
                    return_when=asyncio.FIRST_COMPLETED,
                )
                tasks = list(pending)  # Обновляем список, оставляя незавершённые задачи
        if wallet is None:
            # Ждём завершения всех оставшихся задач
            if tasks:
                await asyncio.gather(*tasks)
            logger.debug(f"Задача обновления завершена")
            return


async def _update_wallets_data(wallets):
    logger.debug(f"Начинаем обновление кошельков")
    last_check = start = now()
    for wallet in wallets:
        wallet.last_stats_check = last_check
    excluded_fields = [
        "id",
        "wallet_id",
        "created_at",
    ]

    await asyncio.gather(
        _update_wallets(wallets),
        _update_wallet_stats_7d([wallet.stats_7d for wallet in wallets], excluded_fields),
        _update_wallet_stats_30d([wallet.stats_30d for wallet in wallets], excluded_fields),
        _update_wallet_stats_all([wallet.stats_all for wallet in wallets], excluded_fields),
    )

    elapsed_time = now() - start
    logger.debug(f"Обновили {len(wallets)} кошельков в базе! | Время: {elapsed_time}")


async def _update_wallet_stats_7d(stats, excluded_fields):
    async with AsyncSessionLocal() as session:
        await SQLAlchemyWalletStatistic7dRepository(session).bulk_update(
            stats,
            excluded_fields=excluded_fields,
        )
        await session.commit()


async def _update_wallet_stats_30d(stats, excluded_fields):
    async with AsyncSessionLocal() as session:
        await SQLAlchemyWalletStatistic30dRepository(session).bulk_update(
            stats,
            excluded_fields=excluded_fields,
        )
        await session.commit()


async def _update_wallet_stats_all(stats, excluded_fields):
    async with AsyncSessionLocal() as session:
        await SQLAlchemyWalletStatisticAllRepository(session).bulk_update(
            stats,
            excluded_fields=excluded_fields,
        )
        await session.commit()


async def _update_wallets(wallets):
    for i in range(5):
        try:
            async with AsyncSessionLocal() as session:
                await SQLAlchemyWalletRepository(session).bulk_update(
                    wallets,
                    fields=["last_stats_check", "is_bot", "is_scammer"],
                )
                await session.commit()
                break
        except DBAPIError as e:
            logger.error(f"Deadlock при обновлении кошельков: {e}")
            await asyncio.sleep(random.randint(1, 3))
    else:
        raise ValueError("Не удалось обновить кошельки после 5 попыток")


async def log_statistics(
    wallets_count,
    tokens_count,
    elapsed_time,
    total_wallets_processed,
    total_tokens_processed,
    total_elapsed_time,
):
    t = int(tokens_count / elapsed_time * 60)
    w = int(wallets_count / elapsed_time * 60)

    logger.info(
        " | ".join(
            [
                f"Процесс обновления кошельков завершен!",
                f"Кол-во: {wallets_count}",
                f"Токенов: {tokens_count}",
                f"Время: {round(elapsed_time, 2)} сек",
                f"В минуту: ({w} / {t})",
            ]
        )
    )

    total_wallets_processed += wallets_count
    total_tokens_processed += tokens_count
    total_elapsed_time += elapsed_time

    total_w = int(total_wallets_processed / total_elapsed_time * 60)
    total_t = int(total_tokens_processed / total_elapsed_time * 60)

    logger.info(
        " | ".join(
            [
                f"Суммарная статистика",
                f"Кошельков: {total_wallets_processed}",
                f"Токенов: {total_tokens_processed}",
                f"Время: {round(total_elapsed_time/60, 2)} мин",
                f"В минуту: ({total_w} / {total_t})",
            ]
        )
    )

    return (
        total_wallets_processed,
        total_tokens_processed,
        total_elapsed_time,
    )


async def process_update_wallet_statistics():
    try:
        await init_db_async()
        received_wallets_queue = Queue()
        fetched_wallets_queue = Queue()
        calculated_wallets_queue = Queue()
        wallets_count = 300_000
        total_wallets_processed = 0
        total_tokens_processed = 0
        total_elapsed_time = 0
        while True:
            start = datetime.now()
            # Получаем кошельки для обновления из БД
            await receive_wallets_from_db(
                received_wallets_queue,
                count=wallets_count,
            )
            # Запускаем обработку кошельков
            async with asyncio.TaskGroup() as tg:
                tg.create_task(
                    fetch_wallets_related_data(
                        received_wallets_queue,
                        fetched_wallets_queue,
                        batch_size=1000,
                        max_parallel=5,
                    )
                )
                calc_task = tg.create_task(
                    calculate_wallets(
                        fetched_wallets_queue,
                        calculated_wallets_queue,
                    )
                )
                tg.create_task(
                    update_wallets(
                        calculated_wallets_queue,
                        batch_size=5000,
                        max_parallel=3,
                    )
                )
            end = datetime.now()
            tokens_count = calc_task.result()
            elapsed_time = (end - start).total_seconds()

            (
                total_wallets_processed,
                total_tokens_processed,
                total_elapsed_time,
            ) = await log_statistics(
                wallets_count,
                tokens_count,
                elapsed_time,
                total_wallets_processed,
                total_tokens_processed,
                total_elapsed_time,
            )
    finally:
        await Tortoise.close_connections()


if __name__ == "__main__":
    asyncio.run(process_update_wallet_statistics())
