import logging
import warnings

import pytz

from src.application.processes.swaps_loader_bitquery.config import API_KEYS
from src.application.processes.swaps_loader_bitquery.extractor import BitqueryError

warnings.filterwarnings(
    "ignore",
    message=".*pydantic.error_wrappers:ValidationError.*",
    category=UserWarning,
)

import asyncio
from asyncio import Queue
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from functools import partial

from pydantic.error_wrappers import ValidationError

from src.application.processes.swaps_loader_bitquery import config, extractor, loader, transformer
from src.application.processes.swaps_loader_bitquery.common import utils
from src.application.processes.swaps_loader_bitquery.common.logger import root_logger as logger


current_api_key_index = 0


def get_next_api_key():
    global current_api_key_index
    try:
        if current_api_key_index + 1 > len(API_KEYS) - 1:
            current_api_key_index = 0
        else:
            current_api_key_index += 1
        res = API_KEYS[current_api_key_index]
        return res
    except Exception:
        return None


def get_current_api_key():
    global current_api_key_index
    try:
        res = API_KEYS[current_api_key_index]
        return res
    except Exception:
        return None


async def extract_process(
        extracted_data_queue: Queue,
        loader_signals_queue: Queue,
        period_start: datetime,
        period_end: datetime,
):
    api_key = get_current_api_key()
    if not api_key:
        raise ValueError(f"Нету доступных api ключей bitquery")

    current_time = period_start
    while current_time < period_end:
        load_next = await loader_signals_queue.get()
        logger.info("Получили сигнал NEXT")

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
            extracted_data = await extract_data_for_period(current_time, next_time, api_key)
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
            await extracted_data_queue.put(
                [
                    extracted_data,
                    current_time,
                    next_time,
                    sol_prices,
                ]
            )
            current_time = next_time
        except BitqueryError as e:
            if "Payment Required" in str(e):
                api_key = get_next_api_key()
                if not api_key:
                    continue
                    # raise ValueError(f"Нету доступных api ключей bitquery") from e

            logger.error(f"Ошибка запроса к Bitquery: {e}")
            await loader_signals_queue.put("EXTRACT NEXT")
            await asyncio.sleep(60)
            continue
        except Exception as e:
            logger.exception(e)
            raise

    await extracted_data_queue.put(None)
    logger.info(f"Сборщик свапов завершил работу")


async def extract_data_for_period(
        start_time: datetime,
        end_time: datetime,
        api_key,
) -> list[dict]:
    workers_count = config.EXTRACTOR_PARALLEL_WORKERS
    intervals = utils.split_time_range(start_time, end_time, workers_count)
    swaps = []

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
                    api_key,
                ),
            )
            for start, end in intervals
        ]
        results = await asyncio.gather(*tasks)

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
            logger.info(f"Время преобразования: {end - start}")
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
            logger.info(f"Время импорта: {end - start}")
        else:
            break
    logger.info(f"Загрузчик завершил работу!")


async def process():
    start_time, end_time = await config.get_period_to_process()

    if start_time <= datetime.now(pytz.UTC) - timedelta(hours=8):
        raise ValueError(
            f"Невозможно начать сбор данных, т.к время начала более 8 часов назад (realtime-db)")

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
