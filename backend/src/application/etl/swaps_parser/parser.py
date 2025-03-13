import asyncio
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timedelta
from functools import partial
from pathlib import Path

import pytz
from flipside.errors.query_run_errors import QueryRunCancelledError, QueryRunExecutionError
from pydantic.error_wrappers import ValidationError
from tortoise import Tortoise
from tortoise.transactions import in_transaction

from src.infra.db.models.tortoise import Token, Wallet, WalletToken
from src.infra.db.setup_tortoise import init_db_async

from . import calculations, db_utils, mappers, utils
from .flipside_queries import get_swaps, get_swaps_jupiter
from .logger import logger

BASE_DIR = Path(__file__).parent

with open(BASE_DIR / "tokens_blacklist.txt", "r") as file:
    BLACKLISTED_TOKENS = [line.strip() for line in file.readlines()]


def fetch_data_for_period(
    start_time,
    end_time,
    flipside_apikey,
    is_jupiter=False,
):
    offset = 0
    limit = 100000
    all_swaps = []
    all_count = 0
    stop = False
    while not stop:
        if is_jupiter:
            logger.debug(f"Собираем данные Jupiter за {start_time} - {end_time} | offset: {offset}")
            swaps, count = get_swaps_jupiter(
                flipside_apikey,
                start_time,
                end_time,
                offset=offset,
                limit=limit,
            )
        else:
            logger.debug(f"Собираем данные за {start_time} - {end_time} | offset: {offset}")
            swaps, count = get_swaps(
                flipside_apikey,
                start_time,
                end_time,
                offset=offset,
                limit=limit,
            )

        all_swaps.extend(swaps)
        all_count += count
        if count < limit:
            stop = True
        else:
            offset += limit

    return all_swaps, all_count, is_jupiter


async def import_data_to_db(wallets, tokens, activities):
    mapped_data = mappers.map_data_by_wallets(
        wallets,
        tokens,
        activities,
    )

    created_wallets, created_tokens = await asyncio.gather(
        db_utils.import_wallets_data(wallets, mapped_data),
        db_utils.import_tokens(tokens),
    )

    logger.info("Кошельки импортированы")
    logger.info("Токены импортированы")

    mappers.update_mapped_data(mapped_data, created_wallets, created_tokens)

    token_wallet_list = mappers.create_wallet_token_ids_list(activities)
    wallet_tokens: list[WalletToken] = await db_utils.load_wallet_tokens(token_wallet_list)
    logger.info(f"WalletToken-статистики загружены")

    # Создаем маппинг ID -> address
    wallet_id_to_address = {w.id: w.address for w in created_wallets}
    token_id_to_address = {t.id: t.address for t in created_tokens}

    for stats in wallet_tokens:
        wallet_address = wallet_id_to_address[stats.wallet_id]
        token_address = token_id_to_address[stats.token_id]
        mapped_data[wallet_address]["tokens"][token_address]["stats"] = stats

    calculations.recalculate_wallet_token_stats(mapped_data)
    logger.info(f"WalletToken-статистики пересчитаны")

    wt_stats = [
        token_data["stats"] for wallet_data in mapped_data.values() for token_data in wallet_data["tokens"].values()
    ]

    # Импортируем активности и статистики обязательно в транзакции!
    async with in_transaction():
        await db_utils.import_activities(activities)
        await db_utils.import_wallet_tokens(wt_stats)
    logger.info(f"Активности импортированы")
    logger.info(f"WalletToken-статистики импортированы")

    logger.info(f"Импортировали данные")
    logger.info(f"Свапов: {len(activities)}")
    logger.info(f"Кошельков: {len(wallets)}")
    logger.info(f"Токенов: {len(tokens)}")
    logger.info(f"Кошелек-токен стат.: {len(wt_stats)}")


async def process_period(
    start_time,
    end_time,
    sol_prices,
    flipside_account,
):
    start_parsing = datetime.now()
    logger.info(f"-" * 50)
    logger.info(f"-" * 50)
    logger.info(f"Начинаем сбор свапов за {start_time} - {end_time}")

    intervals = utils.split_time_range(start_time, end_time, 12)
    intervals_jupiter = utils.split_time_range(start_time, end_time, 4)
    swaps = []
    swaps_jupiter = []
    try:
        loop = asyncio.get_running_loop()
        with ProcessPoolExecutor(max_workers=16) as executor:
            # Создаем задачи для каждого интервала
            tasks = [
                loop.run_in_executor(
                    executor,
                    partial(
                        fetch_data_for_period,
                        start,
                        end,
                        flipside_account.api_key,
                    ),
                )
                for start, end in intervals
            ]
            tasks.extend(
                [
                    loop.run_in_executor(
                        executor,
                        partial(
                            fetch_data_for_period,
                            start,
                            end,
                            flipside_account.api_key,
                            is_jupiter=True,
                        ),
                    )
                    for start, end in intervals_jupiter
                ]
            )
            # Ждем завершения всех задач
            results = await asyncio.gather(*tasks)
    except ValidationError as e:
        logger.error(e)
        raise ValueError("Flipside Error")

    for (
        _swaps,
        _swaps_count,
        is_jupiter,
    ) in results:
        if is_jupiter:
            swaps_jupiter.extend(_swaps)
        else:
            swaps.extend(_swaps)

    ez_dex_count = len(swaps)
    jup_count = len(swaps_jupiter)
    logger.info(f"Собрано свапов: ez_dex - {ez_dex_count} | Jupiter - {jup_count}")
    total_count = ez_dex_count + jup_count
    if total_count == 0:
        return

    logger.info(f"Начинаем создание обьектов")
    start_building = datetime.now()
    all_swaps = utils.combine_swaps(swaps, swaps_jupiter)
    filtered_swaps = utils.filter_swaps(all_swaps, BLACKLISTED_TOKENS)
    extracted = utils.extract_and_build_objects(filtered_swaps, sol_prices)

    logger.info(f"Начинаем импорт данных в БД")
    start_import = datetime.now()
    await import_data_to_db(*extracted)
    end = datetime.now()
    logger.info(
        " | ".join(
            [
                f"Время общее: {end - start_parsing}",
                f"Парсинг: {start_building - start_parsing}",
                f"Создание объектов: {start_import - start_building}",
                f"Импорт: {end - start_import}",
            ]
        )
    )


async def _process():
    try:
        flipside_config = await db_utils.get_flipside_config()
        if not flipside_config:
            logger.error(f"Не найден FlipsideCrypto-конфиг в БД")
            return

        start_time, end_time = get_start_end_time(flipside_config)
        logger.info(f"Запущен сбор данных за период: {start_time} | {end_time}")

        current_time = start_time
        while current_time < end_time:
            next_time = current_time + timedelta(minutes=60)  # Максимальный диапазон за запрос
            if next_time > end_time:
                next_time = end_time

            flipside_account = await db_utils.get_flipside_account()
            if not flipside_account:
                logger.error(f"Нету активных аккаунтов FlipsideCrypto в БД")
                return

            sol_prices = await db_utils.get_sol_prices(
                minute_from=current_time - timedelta(minutes=1),
                minute_to=next_time + timedelta(minutes=1),
            )
            if not sol_prices.get(next_time):
                logger.error(f"Ошибка: Нету данных о цене соланы в {next_time}!")
                return

            try:
                await process_period(
                    current_time,
                    next_time,
                    sol_prices,
                    flipside_account,
                )
                await db_utils.update_flipside_config_swaps_parsed_untill(
                    flipside_config,
                    parsed_untill=next_time,
                )
                current_time = next_time
            except (
                QueryRunExecutionError,
                QueryRunCancelledError,
                ValueError,
            ) as e:
                if isinstance(e, ValueError) and "Flipside Error" not in str(e):
                    raise e
                logger.error(type(e))
                logger.error(f"Меняем учетку Flipside - {str(e)}")
                await db_utils.set_flipside_account_inactive(flipside_account)
    except Exception as e:
        logger.error(f"Error: {e}")
        raise e


def get_start_end_time(flipside_config):
    utc_tz = pytz.timezone("UTC")
    last_tx_inserted_timestamp = flipside_config.swaps_parsed_untill_inserted_timestamp
    start_time = last_tx_inserted_timestamp.astimezone(utc_tz)
    end_time = datetime.now(utc_tz) - timedelta(minutes=1440)
    end_time = end_time.replace(second=0, microsecond=0)
    return start_time, end_time


# def get_start_end_time(flipside_config):
#     utc_tz = pytz.timezone('UTC')
#     _start_time = "2025-02-18 10:45:00"
#     start_time = utc_tz.localize(datetime.strptime(_start_time, "%Y-%m-%d %H:%M:%S"))
#     _end_time = "2025-02-18 10:45:00"
#     end_time = utc_tz.localize(datetime.strptime(_end_time, "%Y-%m-%d %H:%M:%S"))
#     end_time = end_time.replace(second=0, microsecond=0)
#     return start_time, end_time


# TODO: в идеале переделать парсинг по INSERTED_TMESTAMP а не по BLOCK_TIMESTAMP
#  чтобы исключить пропуски


async def process():
    await init_db_async()
    try:
        await _process()
    finally:
        await Tortoise.close_connections()
