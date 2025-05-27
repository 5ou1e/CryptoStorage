import logging
import warnings

from sqlalchemy import select

from src.infra.db.sqlalchemy.setup import AsyncSessionMaker

warnings.filterwarnings(
    "ignore",
    message=".*pydantic.error_wrappers:ValidationError.*",
    category=UserWarning,
)
import asyncio
from asyncio import Queue
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from datetime import datetime, timedelta
from functools import partial

from flipside.errors.query_run_errors import QueryRunCancelledError, QueryRunExecutionError
from pydantic.error_wrappers import ValidationError

from src.domain.entities import Swap

from . import config, extractor, loader, transformer
from .common import utils
from .extractor import FlipsideClientException

logger = logging.getLogger(__name__)


async def extract_process(
    extracted_data_queue: Queue,
    loader_signals_queue: Queue,
    period_start: datetime,
    period_end: datetime,
):
    current_time = period_start
    while current_time < period_end:
        load_next = await loader_signals_queue.get()
        logger.info("Получили сигнал NEXT")
        flipside_account = await utils.get_flipside_account()
        if not flipside_account:
            logger.error(f"Нету активных аккаунтов FlipsideCrypto в БД")
            break

        next_time = min(
            current_time + timedelta(minutes=config.EXTRACTOR_PERIOD_INTERVAL_MINUTES),
            period_end,
        )  # Максимальный диапазон за запрос

        sol_prices = await utils.get_sol_prices(
            minute_from=current_time - timedelta(minutes=1),
            minute_to=next_time + timedelta(minutes=1),
        )
        if not sol_prices.get(next_time):
            logger.error(f"Ошибка - Нету данных о цене соланы в {next_time}!")
            break
        try:
            logger.info(f"Начинаем сбор свапов за {current_time} - {next_time}")
            start = datetime.now()
            result = await asyncio.gather(
                *[
                    extract_data_for_period(current_time, next_time, flipside_account.api_key),
                    load_swaps_from_db(current_time, next_time),
                ]
            )
            extracted_data = result[0]
            swaps_from_db = result[1]
            logger.info(f"Свапов из бд: {len(swaps_from_db)}")
            total_count = len(extracted_data)
            end = datetime.now()
            logger.info(
                " | ".join(
                    [
                        f"Собраны свапы за период {current_time} - {next_time}",
                        f"Кол-во: {total_count}",
                        f"Время {end - start}",
                    ]
                )
            )

            tx_hashes = {swap["tx_id"] for swap in extracted_data}
            swaps_to_delete = []
            for swap in swaps_from_db:
                if swap.tx_hash in tx_hashes:
                    swaps_to_delete.append(swap)
            logger.info(f"Свапов к удалению - {len(swaps_to_delete)}")

            # for swap in swaps_to_delete:
            #     print(swap.tx_hash, swap.token_id)
            await extracted_data_queue.put(
                [
                    swaps_to_delete,
                    current_time,
                    next_time,
                    sol_prices,
                ]
            )
            current_time = next_time
        except (
            QueryRunExecutionError,
            QueryRunCancelledError,
            FlipsideClientException,
        ) as e:
            await utils.set_flipside_account_inactive(flipside_account)
            logger.error(f"Ошибка Flipside: {e}")
            logger.info(f"Меняем учетку Flipside")
            await loader_signals_queue.put("EXTRACT NEXT")
            continue

    await extracted_data_queue.put(None)
    logger.info(f"Сборщик свапов завершил работу")


async def load_swaps_from_db(start, end):
    from src.infra.db.sqlalchemy.models import Swap as SwapModel

    async with AsyncSessionMaker() as session:
        query = select(*SwapModel.__table__.columns).where((SwapModel.timestamp >= start) & (SwapModel.timestamp < end))
        result = await session.execute(query)
        # for row in result.mappings().all():
        #     print(row)
        swaps = [Swap(**row) for row in result.mappings().all()]
        return swaps


async def extract_data_for_period(
    start_time: datetime,
    end_time: datetime,
    flipside_api_key,
) -> list[dict]:
    workers_count = config.EXTRACTOR_PARALLEL_WORKERS
    intervals = utils.split_time_range(start_time, end_time, workers_count)
    swaps = []
    try:
        loop = asyncio.get_running_loop()
        with ThreadPoolExecutor(max_workers=workers_count) as executor:
            # Создаем задачи для каждого интервала
            tasks = [
                loop.run_in_executor(
                    executor,
                    partial(
                        extractor.fetch_data_for_period,
                        start,
                        end,
                        flipside_api_key,
                    ),
                )
                for start, end in intervals
            ]
            results = await asyncio.gather(*tasks)
    except ValidationError as e:
        raise FlipsideClientException(f"Flipside Error {e}") from e

    for _swaps in results:
        swaps.extend(_swaps)

    return swaps


async def transform_process(
    extracted_data_queue: Queue,
    transformed_data_queue: Queue,
):

    while True:
        data = await extracted_data_queue.get()
        if data is not None:
            swaps, period_start, period_end, sol_prices = data
            logger.info(f"Начинаем преобразование данных")
            start = datetime.now()
            objects_to_load = await asyncio.to_thread(transformer.transform_data, swaps, sol_prices)
            end = datetime.now()
            logger.info(f"Время преобразования: {end-start}")
            await transformed_data_queue.put([objects_to_load, period_start, period_end])
        else:
            break
    await transformed_data_queue.put(None)  # Кладем None чтобы остальные процессы завершали работу
    logger.info(f"Преобразователь завершил работу!")


async def load_process(
    transformed_data_queue: Queue,
    loader_signals_queue: Queue,
):
    while True:
        data = await transformed_data_queue.get()
        if data is not None:
            await loader_signals_queue.put("EXTRACT NEXT")
            objects_to_load, period_start, period_end = data
            logger.info(f"Начинаем импорт данных в БД")
            start = datetime.now()
            await loader.load_data_to_db(*objects_to_load, period_end)
            end = datetime.now()
            logger.info(f"Данные импортированы за {period_start} - {period_end}")
            logger.info(f"Время импорта: {end-start}")
        else:
            break
    logger.info(f"Загрузчик завершил работу!")


async def process():
    start_time, end_time = await config.get_period_to_process()
    logger.info(f"Запущен процесс для периода c {start_time} до {end_time}")

    extracted_data_queue = Queue()
    transformed_data_queue = Queue()
    loader_signals_queue = Queue()  # Очередь сигналов, чтобы подгружать новые, только когда загрузчик забрал предыдущие

    await loader_signals_queue.put("EXTRACT NEXT")

    try:
        async with asyncio.TaskGroup() as tg:
            tg.create_task(
                extract_process(
                    extracted_data_queue,
                    loader_signals_queue,
                    start_time,
                    end_time,
                )
            )
            tg.create_task(transform_process(extracted_data_queue, transformed_data_queue))
            tg.create_task(load_process(transformed_data_queue, loader_signals_queue))
    except Exception as e:
        logger.critical(f"Неизвестная ошибка, завершаем работу: {e}")
        raise
    logger.info(f"Процесс для периода c {start_time} до {end_time} завершен!")


async def main():
    if config.PERSISTENT_MODE:
        while True:
            await process()
            await asyncio.sleep(config.PROCESS_INTERVAL_SECONDS)
    else:
        await process()  # Запуск только один раз, если статичный конфиг


if __name__ == "__main__":
    asyncio.run(main())
