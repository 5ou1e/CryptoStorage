import asyncio
import logging
from asyncio import Queue
from datetime import datetime, timedelta, timezone

import pytz
from tortoise import Tortoise
from tortoise.timezone import now
from tortoise.transactions import in_transaction

from src.domain.entities.wallet import (
    WalletDetailEntity,
    WalletEntity,
    WalletStatistic7dEntity,
    WalletStatistic30dEntity,
    WalletStatisticAllEntity,
    WalletTokenEntity,
)
from src.infra.db.models.tortoise import (
    Wallet,
    WalletToken,
)
from src.infra.db.repositories.tortoise import (
    TortoiseWalletDetailRepository,
    TortoiseWalletRepository,
    TortoiseWalletStatistic7dRepository,
    TortoiseWalletStatistic30dRepository,
    TortoiseWalletStatisticAllRepository,
)
from src.infra.db.setup_tortoise import (
    init_db_async,
)

from .utils import (
    filter_period_tokens,
    recalculate_wallet_period_stats,
)

logger = logging.getLogger("tasks.update_wallet_statistics")


async def update_single_wallet_statistics(
    wallet_id,
):
    # # TODO отрефакторить
    pass
    # try:
    #     await init_db_async()
    #     wallet = await Wallet.get_or_none(id=wallet_id).prefetch_related(
    #         "details", "stats_7d", "stats_30d", "stats_all"
    #     )
    #     if not wallet:
    #         logger.info(f"Кошелька {wallet_id} не существует!")
    #     logger.info(f"Достали кошелек из бд - {wallet}")
    #     await process_wallets([wallet])
    # finally:
    #     await Tortoise.close_connections()


async def receive_wallets_from_db(
    received_wallets_queue: Queue,
    count: int,
):
    """Загрузка данных из БД и помещение в очередь"""
    logger.info(f"Начинаем получение кошельков из БД")
    t1 = datetime.now()
    wallets: list[WalletEntity] = await TortoiseWalletRepository().get_wallets_for_update_stats(count=count)
    t2 = datetime.now()
    logger.info(f"Получили {len(wallets)} кошельков из БД | Время: {t2 - t1}")
    # Вместо того чтобы фетчить с БД просто создаем временные обьекты
    for wallet in wallets:
        wallet.details = WalletDetailEntity(wallet_id=wallet.id)
        wallet.stats_7d = WalletStatistic7dEntity(wallet_id=wallet.id)
        wallet.stats_30d = WalletStatistic30dEntity(wallet_id=wallet.id)
        wallet.stats_all = WalletStatisticAllEntity(wallet_id=wallet.id)
    t3 = datetime.now()
    logger.debug(f"Создали связанные обьекты кошельков | Время: {t3 - t2}")
    for wallet in wallets:
        await received_wallets_queue.put(wallet)
    await received_wallets_queue.put(None)


async def fetch_wallet_tokens(
    received_wallets_queue: Queue,
    fetched_wallets_queue: Queue,
    batch_size: int,
    max_parallel: int = 5,
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
        max_parallel (int, optional): Максимальное количество параллельных задач. По умолчанию 5.
    """
    batch = []
    tasks = []  # Список активных задач обработки батчей
    while True:
        wallet: WalletEntity | None = await received_wallets_queue.get()
        if wallet is not None:
            batch.append(wallet)
        # Если набрали батч нужного размера или пришёл сигнал завершения (wallet is None)
        if (len(batch) >= batch_size) or (wallet is None and batch):
            # Создаём копию батча для передачи в задачу
            tasks.append(
                asyncio.create_task(
                    _fetch_tokens(
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


async def _fetch_tokens(
    wallets: list[WalletEntity],
    fetched_wallets_queue: Queue,
):
    # Загружаем связанные токены для кошельков
    # TODO: использовать метод репозитория
    # wallet_tokens = await WalletTokenRepository().get(
    #     filter_by={
    #         "wallet_id__in": [wallet.id for wallet in wallets]
    #     }
    # )
    start = datetime.now()
    wallet_tokens = await WalletToken.filter(wallet_id__in=[wallet.id for wallet in wallets]).all().values()
    end = datetime.now()
    wt_count = len(wallet_tokens)
    logger.info(f"Подгрузили токены {len(wallets)} кошельков из БД | Токенов: {wt_count} | Время: {end-start}")
    start = datetime.now()
    wallet_dict = {wallet.id: wallet for wallet in wallets}
    # Мапим токены по кошелькам
    for token in wallet_tokens:
        wallet = wallet_dict.get(token["wallet_id"])
        if wallet:
            # Добавляем токен
            wallet.tokens.append(WalletTokenEntity(**token))
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
    cnt = 0
    while True:
        wallet: WalletEntity | None = await received_wallets_queue.get()
        if wallet:
            start = datetime.now()
            await calculate_wallet(wallet)
            tokens_count += len(wallet.tokens)
            end = datetime.now()
            cnt += 1
            spent_time += end - start
            if cnt >= 10000:
                logger.debug(f"Пересчет {cnt} занял ~ {spent_time}")
                spent_time = timedelta(minutes=0)
                cnt = 0
            await calculated_wallets_queue.put(wallet)
        else:
            await calculated_wallets_queue.put(None)
            logger.debug(f"Задача пересчета завершена")
            return tokens_count


async def update_wallets(
    calculated_wallets_queue: Queue,
    batch_size: int,
    max_parallel: int = 5,
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
        wallet: WalletEntity | None = await calculated_wallets_queue.get()
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
    logger.info(f"Начинаем обновление кошельков")
    start = now()
    wallet_stats_7d = [wallet.stats_7d for wallet in wallets]
    wallet_stats_30d = [wallet.stats_30d for wallet in wallets]
    # Обновляем статистику "за все время" только нужным кошелькам
    wallet_stats_all = [wallet.stats_all for wallet in wallets]  # if wallet.is_need_update_stats_all
    wallets_details = [wallet.details for wallet in wallets]  # if wallet.is_need_update_stats_all
    logger.info(f"{len(wallet_stats_all)}, {len(wallets_details)}")
    exclude = [
        "id",
        "wallet_id",
        "token_id",
        "created_at",
        "updated_at",
    ]
    last_check = now()
    for wallet in wallets:
        wallet.last_stats_check = last_check

    await asyncio.gather(
        TortoiseWalletStatistic7dRepository().bulk_update(
            wallet_stats_7d,
            excluded_fields=exclude,
            id_column="wallet_id",
        ),
        TortoiseWalletStatistic30dRepository().bulk_update(
            wallet_stats_30d,
            excluded_fields=exclude,
            id_column="wallet_id",
        ),
        TortoiseWalletStatisticAllRepository().bulk_update(
            wallet_stats_all,
            excluded_fields=exclude,
            id_column="wallet_id",
        ),
        TortoiseWalletDetailRepository().bulk_update(
            wallets_details,
            fields=["is_bot", "is_scammer"],
            excluded_fields=["id", "updated_at"],
            id_column="wallet_id",
        ),
        # Wallet.filter(
        #     id__in=[wallet.id for wallet in wallets]
        # ).update(
        #     last_stats_check=now()
        # ),
        # TODO: убрать обновление поля first_activity_timestamp
        _update_wallets(wallets),
    )

    elapsed_time = now() - start
    logger.info(f"Обновили {len(wallets)} кошельков в базе! | Время: {elapsed_time}")


async def _update_wallets(wallets):
    async with in_transaction() as conn:
        # !!!Сортируем по адресу, чтобы избежать дедлоков при массовом апдейте
        # wallets.sort(key=lambda w: w.address)
        # q = Wallet.filter(
        #     id__in=[wallet.id for wallet in wallets]
        # ).select_for_update().order_by("address").all()
        # # logger.error(q.sql())
        # await q
        await TortoiseWalletRepository().bulk_update(
            wallets,
            fields=[
                "first_activity_timestamp",
                "last_stats_check",
            ],
        )


async def calculate_wallet(wallet):
    wallet_tokens = wallet.tokens
    wallet_tokens_count = len(wallet_tokens)
    await recalculate_wallet_stats(wallet, wallet_tokens)
    logger.debug(f"Посчитали статистику кошелька {wallet.id}")
    return wallet_tokens_count


async def recalculate_wallet_stats(wallet, all_tokens):
    periods = [7, 30, 0]
    current_datetime = datetime.now().astimezone(tz=pytz.UTC)
    for period in periods:
        if period == 7:
            stats = wallet.stats_7d
        elif period == 30:
            stats = wallet.stats_30d
        else:
            # if not wallet.is_need_update_stats_all:
            #     continue
            stats = wallet.stats_all
        token_stats = await filter_period_tokens(all_tokens, period, current_datetime)
        await recalculate_wallet_period_stats(stats, token_stats)

    # if wallet.is_need_update_stats_all:
    wallet_details = wallet.details
    wallet_details.is_scammer = determine_scammer_status(wallet)
    wallet_details.is_bot = determine_bot_status(wallet)

    b_tkns = [token for token in all_tokens if token.first_buy_timestamp]
    s_tkns = [token for token in all_tokens if token.first_sell_timestamp]
    fb_timestamp = (
        datetime.fromtimestamp(
            min(
                b_tkns,
                key=lambda x: x.first_buy_timestamp,
            ).first_buy_timestamp,
            tz=timezone.utc,
        )
        if b_tkns
        else None
    )

    fs_timestamp = (
        datetime.fromtimestamp(
            min(
                s_tkns,
                key=lambda x: x.first_sell_timestamp,
            ).first_sell_timestamp,
            tz=timezone.utc,
        )
        if s_tkns
        else None
    )

    # Вычисляем first_activity_timestamp, исключая None
    if fb_timestamp and fs_timestamp:
        first_activity_timestamp = min(fb_timestamp, fs_timestamp)
    else:
        first_activity_timestamp = fb_timestamp or fs_timestamp  # Берем первое ненулевое значение

    first_activity_timestamp_in_db = wallet.first_activity_timestamp
    if first_activity_timestamp and (
        first_activity_timestamp_in_db is None or first_activity_timestamp < first_activity_timestamp_in_db
    ):
        wallet.first_activity_timestamp = first_activity_timestamp


def determine_scammer_status(
    wallet: Wallet,
) -> bool:
    """Определяем статус скамера"""
    stats_all: WalletStatisticAllEntity | None = wallet.stats_all
    # Если у кошелька более 5 токенов и процент "с продажей без покупки" больше N - помечаем как скамера
    if stats_all.total_token >= 5 and stats_all.token_sell_without_buy / stats_all.total_token >= 0.21:
        return True
    # Если у кошелька более 5 токенов и процент продано>куплено больше N - помечаем как скамера
    if stats_all.total_token >= 5 and stats_all.token_with_sell_amount_gt_buy_amount / stats_all.total_token >= 0.21:
        return True
    # Если у кошелька более 1 акктивности с 3+ трейдерами в одной транзе - помечаем его как скамера
    if stats_all.total_swaps_from_txs_with_mt_3_swappers > 0:
        return True

    return False


def determine_bot_status(
    wallet: WalletEntity,
) -> bool:
    """Определяем статус арбитраж-бота"""
    stats_all: WalletStatisticAllEntity | None = wallet.stats_all
    # Если у кошелька более 50% активностей помечены как арбитражные - помечаем его как арбитраж-бота
    if stats_all.total_buys_and_sales_count > 0:
        if stats_all.total_swaps_from_arbitrage_swap_events / stats_all.total_buys_and_sales_count >= 0.5:
            return True
    # Токенов >= N и среднее время покупки-продажи <= X секунд
    if stats_all.total_token >= 500:
        if (duration := stats_all.token_buy_sell_duration_avg) and duration <= 2:
            return True
    if stats_all.total_token >= 1000:
        # Токенов >= N и средняя сумма покупки менее X
        if (avg_buy_amount := stats_all.token_avg_buy_amount) and avg_buy_amount < 30:
            return True
        # Токенов >= N и соотнешение "всего транзакций / всего токенов" > X
        if stats_all.total_buys_and_sales_count / stats_all.total_token > 10:
            return True

    return False


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
        wallets_count = 100_000
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
                    fetch_wallet_tokens(
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
