import asyncio
import logging
import statistics
import traceback
from datetime import datetime, timedelta

from celery import shared_task
from django.utils.timezone import make_aware, now
from external_services.models import GmgnAPIClientConfig
from external_services.services.gmgn import GmgnAPIClient
from solana.models.tortoise_models.models import Token, Wallet, WalletActivity, WalletTokenStatistic
from tortoise import Tortoise

logger = logging.getLogger('celery')


with open("data/tokens_blacklist.txt", 'r') as file:
    BLACKLISTED_TOKENS = [line.strip() for line in file.readlines()]

@shared_task(bind=True, ignore_result=False)
def process_update_wallet_statistics(self, config_id=2, max_tasks=10):
    logger.info("Задача обновления кошельков запущена!")
    asyncio.run(_process_update_wallet_statistics_async(config_id, max_tasks=max_tasks))


@shared_task(bind=True, ignore_result=False)
def process_update_single_wallet_statistics(self, wallet_id):
    logger.info("Задача обновления 1-го кошелька запущена!")
    asyncio.run(_process_update_single_wallet_statistics(wallet_id))


async def init_tortoise():
    from django.conf import settings
    await Tortoise.init(config=settings.TORTOISE_ORM)
    await Tortoise.generate_schemas()

async def _process_update_single_wallet_statistics(wallet_id):

    await init_tortoise()

    try:
        settings = await GmgnAPIClientConfig.objects.afirst()
        client = GmgnAPIClient(
            proxy=settings.proxy,
            cookies=settings.cookies,
        )
        wallet = await Wallet.get_or_none(id=int(wallet_id))

        if wallet:# and not wallet.stats_check_in_process:
            logger.debug(f"Достали кошелек из бд - {wallet}")
            await process_wallet(client, wallet)
        else:
            logger.debug(f"Кошелька {wallet_id} не существует в БД!")
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        raise e
    finally:
        await client.close()
        await Tortoise.close_connections()


async def _process_update_wallet_statistics_async(config_id, max_tasks=50):
    await init_tortoise()
    tasks = []  # Список для хранения активных задач
    # Получаем настройки для API клиента
    settings = await GmgnAPIClientConfig.objects.aget(id=config_id)
    client = GmgnAPIClient(
        proxy=settings.proxy,
        cookies=settings.cookies,
    )

    # Сбрасываем статус активнной проверки для всех кошельков
    await Wallet.filter(stats_check_in_process=True).update(
        stats_check_in_process=False
    )

    while True:
        # Очищаем завершенные задачи
        tasks = [task for task in tasks if not task.done()]
        # Проверяем, сколько активных задач сейчас выполняется
        active_tasks = len(tasks)
        # Если активных задач меньше 50, пытаемся взять кошелек
        if active_tasks < max_tasks:
            task = asyncio.create_task(process_get_and_update_wallet(client))
            tasks.append(task)
        else:
            # logger.debug("Лимит параллельных задач достигнут. Ожидаем 1 секунду.")
            await asyncio.sleep(1)  # Ждем 1 секунду, если лимит задач достигнут
    await Tortoise.close_connections()
    return "OK"


async def process_get_and_update_wallet(client):
    wallet = await Wallet.get_wallet_for_update_stats()
    if wallet:
        try:
            await process_wallet(client, wallet)
        finally:
            try:
                wallet.stats_check_in_process = False
                await wallet.save()
            except Exception as e:
                logger.error(f"Ошибка при сохранении кошелька {wallet.address}: {e}")

async def process_wallet(client, wallet):
    """Получение данных о кошельке и его новых транзакциях и обновление статистики в БД"""
    try:
        start = now()
        existing_wallet_activities_objects = await WalletActivity.filter(wallet=wallet, ).select_related('token')
        last_activity_timestamp = max([activity.timestamp for activity in existing_wallet_activities_objects], default=None)
        start_parsing = now()
        wallet_data = await client.get_wallet_data(wallet.address)
        if not wallet_data:
            logger.debug(f"Не удалось собрать данные кошелька {wallet.address} =(")
            return

        wallet_activities_data = await client.get_wallet_activities_data(wallet.address, limit=None, from_timestamp=last_activity_timestamp)
        logger.debug(f"Собрали данные кошелька и его транзакций {wallet.address} | транзакзицй - {len(wallet_activities_data)}")
        data = {
            'wallet': wallet,
            'stats': wallet_data,
            'activities': filter_wallet_activities(wallet_activities_data),
        }
        parsing_end = now()
        imported_wallet_activities_count, time1, time2, time3, time4 = await update_wallet_data_db(data, existing_wallet_activities_objects)
        import_end = now()

        logger.info(f"Статистика {wallet.address} успешно обновлена , новых транзакций: {imported_wallet_activities_count}, \
        время парсинга: {parsing_end-start_parsing}, время импорта: {import_end-parsing_end} \
        ( {time1} | {time2} | {time3} | {time4} )")
    except Exception as e:
        logger.error(f"Не удалось обновить статистику кошелька {wallet.address} - {e}")
        logger.error(traceback.format_exc())

async def update_wallet_data_db(wallet_data, existing_wallet_activities_objects):
    start = now()
    wallet = wallet_data['wallet']
    new_activities = wallet_data['activities']

    existing_wallet_activities = await queryset_to_nested_dict_list(existing_wallet_activities_objects)
    new_unique_wallet_activities = await new_activities_excluding_existing(new_activities, existing_wallet_activities)

    logger.debug(f"Новых активностей: {len(new_unique_wallet_activities)}")

    all_wallet_activities = new_unique_wallet_activities + existing_wallet_activities

    token_stats = await aggregate_tokens(all_wallet_activities)
    wallet_period_stats = await calculate_wallet_stats(token_stats)

    # logger.debug(json.dumps(wallet_period_stats, indent=3))

    wallet_data['period_stats'] = wallet_period_stats

    time1 = time2 = time3 = now()
    suitable, reason = await is_wallet_suitable(wallet_data)

    if suitable:  # Пишем в БД только для подходящих кошельков
        try:
            tokens = await Token.bulk_import_tokens_from_wallet_activities(new_unique_wallet_activities)
            time1 = now()
            await WalletActivity.bulk_import_new_wallet_activities(wallet, tokens, new_unique_wallet_activities)
            time2 = now()
            token_stats_to_update = {token: data for token, data in token_stats.items() if token in tokens}
            await WalletTokenStatistic.bulk_import_token_stats(wallet, tokens, token_stats_to_update)
            time3 = now()
            logger.debug(f"Загрузили активности кошелька в базу {wallet.address}")
        except Exception as e:
            logger.error(f"Ошибка при загрузке активностей кошелька {wallet.address} в БД! - {e}")
            logger.error(traceback.format_exc())
    else:
        logger.debug(f"Активности кошелька {wallet.address} не были загружены т.к он не подходит по критериям")

    await WalletStatistic.update_or_create_wallet_stats(wallet_data)
    logger.debug(f"Загрузили статистику кошелька в базу {wallet.address}")
    await update_wallet_db(wallet, wallet_data)

    time4 = now()

    t1 = int((time1 - start).total_seconds())
    t2 = int((time2 - time1).total_seconds())
    t3 = int((time3 - time2).total_seconds())
    t4 = int((time4 - time3).total_seconds())

    return len(new_unique_wallet_activities), t1, t2, t3, t4

async def update_wallet_db(wallet, wallet_data):
    new_stasts_check_time = await get_new_stasts_check_time(wallet, wallet_data)
    wallet.new_stasts_check_time = new_stasts_check_time
    wallet.last_stats_check = now()


async def get_new_stasts_check_time(wallet, wallet_data):
    # Обновляем интервал и дату чека
    wallet_stats = wallet_data['stats']
    stats_all = wallet_data['period_stats'][0]

    interval = timedelta(days=1)

    if stats_all['token_with_buy'] and stats_all['token_with_buy'] >= 20:
        if (stats_all['winrate'] if stats_all['winrate'] else 0) <= 40 and (
                stats_all['total_profit_usd'] if stats_all['total_profit_usd'] else 0) < 1000:
            interval = timedelta(days=7)
    if wallet_stats['sol_balance'] and float(wallet_stats['sol_balance']) < 0.01:
        interval = timedelta(days=7)

    if stats_all['total_token'] >= 5000:
        interval = None

    new_stasts_check_time = (now() + interval) if interval else None

    return new_stasts_check_time

async def is_wallet_suitable(wallet_data):
    stats_30 = wallet_data['period_stats'][30]
    total_token_30 = stats_30['total_token']
    winrate_30 = stats_30['winrate']
    profit_30 = stats_30['total_profit_usd']
    stats_all = wallet_data['period_stats'][0]
    total_token_all = stats_all['total_token']

    if total_token_30 > 50 and profit_30 <= 0:
        return False, "Профит USD меньше 0"
    if total_token_all >= 5000:
        return False, "Слишкмо много токенов (5000)"
    return True, ""


async def queryset_to_nested_dict_list(queryset):
    return [
        {
            'tx_hash': obj.tx_hash,
            'timestamp': obj.timestamp,
            'event_type': obj.event_type,
            'token_amount': obj.token_amount,
            'quote_amount': obj.quote_amount,
            'cost_usd': obj.cost_usd,
            'price_usd': obj.price_usd,
            'token': {
                'id': obj.token.id,
                'address': obj.token.address,
                'name': obj.token.name,
                'symbol': obj.token.symbol,
                'price': obj.token.price,
                'decimals': obj.token.decimals,
                'logo': obj.token.logo,
            } if obj.token else {}
        }
        for obj in queryset
    ]
async def new_activities_excluding_existing(new_activities, existing_wallet_activities):
    new_unique_wallet_activities = []
    existing_keys = set(
        (activity['id'], activity['tx_hash']) for activity in existing_wallet_activities
    )
    for activity in new_activities:
        gmgn_id = activity.get('id', None)
        tx_hash = activity.get('tx_hash', None)

        # Пропускаем активности, которые уже есть в базе данных
        if (gmgn_id, tx_hash) in existing_keys or (not gmgn_id or not tx_hash):
            continue

        new_unique_wallet_activities.append(activity)

    return new_unique_wallet_activities


def filter_wallet_activities(wallet_activities):
    filtered_activities = list(filter(filter_activities, wallet_activities))
    for act in filtered_activities:
        act['token_amount'] = round(float(act['token_amount']), 20) if act['token_amount'] else None
        act['quote_amount'] = round(float(act['quote_amount']), 20) if act['quote_amount'] else None
        act['cost_usd'] = round(float(act['cost_usd']), 20) if act['cost_usd'] else None
        act['buy_cost_usd'] = round(float(act['buy_cost_usd']), 20) if act['buy_cost_usd'] else None
        act['price'] = round(float(act['price']), 20) if act['price'] else None
        act['price_usd'] = round(float(act['price_usd']), 20) if act['price_usd'] else None
    return filtered_activities


def filter_activities(activity):
    token = activity.get("token")
    if not token:
        return False
    token_address = token.get('address')
    if token and token_address:
        if not token_address in BLACKLISTED_TOKENS:
            return True
    return False


async def filter_period_tokens(all_tokens, period, current_datetime):
    if not period == 0:
        days = int(period)
        threshold_date = current_datetime - timedelta(days=days)
        period_tokens = {token: data for token, data in all_tokens.items() if data['stats']["first_buy_timestamp"] and make_aware(datetime.fromtimestamp(int(data['stats']["first_buy_timestamp"]))) >= threshold_date}
        return period_tokens
    return all_tokens


async def calculate_wallet_stats(all_tokens):
    periods = [7, 30, 0]
    stats = {}
    current_datetime = now()
    for period in periods:
        period_stats = await calculate_wallet_period_stats(all_tokens, period, current_datetime)
        stats[period] = period_stats

    return stats


async def calculate_wallet_period_stats(all_tokens, period, current_datetime):
    tokens = await filter_period_tokens(all_tokens, period, current_datetime)
    stats = {
        'total_token': 0,
        'total_token_buys': 0,
        'total_token_sales': 0,
        'total_token_buy_amount_usd': 0,
        'total_token_sell_amount_usd': 0,
        'total_profit_usd': 0,
        'pnl_lt_minus_dot5_num': 0,
        'pnl_minus_dot5_0x_num': 0,
        'pnl_lt_2x_num': 0,
        'pnl_2x_5x_num': 0,
        'pnl_gt_5x_num': 0,

        'token_with_buy': 0,
        'token_with_buy_and_sell': 0,
        'token_buy_without_sell': 0,
        'token_sell_without_buy': 0,
        'token_with_sell_amount_gt_buy_amount': 0,
    }

    profitable_tokens_count = 0
    token_first_buy_sell_duration_values = []
    token_buy_amount_usd_values = []
    token_first_buy_price_values = []

    for token, data in tokens.items():
        token_stats = data['stats']

        stats['total_token'] += 1
        stats['total_token_buys'] += token_stats['total_buys_count']
        stats['total_token_sales'] += token_stats['total_sales_count']
        stats['total_token_buy_amount_usd'] += token_stats['total_buy_amount_usd']
        stats['total_token_sell_amount_usd'] += token_stats['total_sell_amount_usd']
        stats['total_profit_usd'] += token_stats['total_profit_usd']

        if token_stats['total_buys_count'] > 0:
            stats['token_with_buy'] += 1
            if token_stats['first_buy_price_usd']:
                token_first_buy_price_values.append(token_stats['first_buy_price_usd'])
            if token_stats['total_sales_count'] > 0:
                stats['token_with_buy_and_sell'] += 1
            token_buy_amount_usd_values.append(token_stats['total_buy_amount_usd'])

        if token_stats['total_buys_count'] > 0 and token_stats['total_sales_count'] == 0:
            stats['token_buy_without_sell'] += 1
        if token_stats['total_sales_count'] > 0 and token_stats['total_buys_count'] == 0:
            stats['token_sell_without_buy'] += 1

        if token_stats['total_sell_amount_token'] > token_stats['total_buy_amount_token']:
            stats['token_with_sell_amount_gt_buy_amount'] += 1

        if token_stats['first_buy_sell_duration']:
            token_first_buy_sell_duration_values.append(token_stats['first_buy_sell_duration'])

        profit_percent = token_stats['total_profit_percent']
        if token_stats['total_buys_count'] > 0:
            if token_stats['total_profit_usd'] >= 0:
                profitable_tokens_count += 1
                if profit_percent:
                    if profit_percent >= 500:
                        stats['pnl_gt_5x_num'] += 1
                    elif profit_percent >= 200:
                        stats['pnl_2x_5x_num'] += 1
                    else:
                        stats['pnl_lt_2x_num'] += 1
            else:
                if profit_percent:
                    if profit_percent <= -50:
                        stats['pnl_lt_minus_dot5_num'] += 1
                    else:
                        stats['pnl_minus_dot5_0x_num'] += 1

    stats['token_buy_sell_duration_avg'] = round(
        sum(token_first_buy_sell_duration_values) / stats['token_with_buy_and_sell'],
        0) if stats['token_with_buy_and_sell'] else None
    stats['total_profit_multiplier'] = round(
        stats['total_profit_usd'] / stats['total_token_buy_amount_usd']*100, 2) if stats[
        'total_token_buy_amount_usd'] else None  # Только для токенов у которых была покупка!
    stats['token_avg_buy_amount'] = round(
        stats['total_token_buy_amount_usd'] / stats['token_with_buy'], 5) if stats['token_with_buy'] else None
    stats['token_first_buy_avg_price_usd'] = round(sum(token_first_buy_price_values) / stats['token_with_buy'],
                                                   20) if stats['token_with_buy'] else None
    stats['token_first_buy_median_price_usd'] = statistics.median(
        token_first_buy_price_values) if token_first_buy_price_values else None
    stats['token_avg_profit_usd'] = round(
        stats['total_profit_usd'] / stats['token_with_buy'],
        2) if stats['token_with_buy'] else None  # Только для токенов у которых была покупка!
    stats['winrate'] = round(profitable_tokens_count / stats['token_with_buy'] * 100,
                             2) if stats['token_with_buy'] else None  # Только для токенов у которых была покупка!

    stats['token_buy_sell_duration_median'] = round(statistics.median(token_first_buy_sell_duration_values),
                                                    0) if token_first_buy_sell_duration_values else None
    stats['token_median_buy_amount'] = round(statistics.median(token_buy_amount_usd_values),
                                                 20) if token_buy_amount_usd_values else None

    return stats

async def aggregate_tokens(wallet_activities: list) -> dict:
    tokens = {}
    for transaction in wallet_activities:
        token_address = transaction['token']['address']  # Извлечение адреса токена
        if token_address not in tokens:
            tokens[token_address] = {'activities': []}  # Создаем ключ, если его еще нет
        tokens[token_address]['activities'].append(transaction)  # Добавляем транзакцию

    for token, data in tokens.items():
        stats = await calculate_token_stats(data['activities'])
        data['stats'] = stats

    return tokens


async def calculate_token_stats(token_activities: list) -> dict:
    stats = {
        'total_buys_count': 0,
        'total_buy_amount_usd': 0,
        'total_buy_amount_token': 0,
        'first_buy_price_usd': None,
        'first_buy_timestamp': None,

        'total_sales_count': 0,
        'total_sell_amount_usd': 0,
        'total_sell_amount_token': 0,
        'first_sell_price_usd': None,
        'first_sell_timestamp': None,

        'last_activity_timestamp': None,

        'total_profit_usd': 0,
        'first_buy_sell_duration': None,
        'total_profit_percent': None,  # Только для токенов у которых была покупка!

    }

    first_buy = None
    first_sell = None
    last_activity = None

    for activity in token_activities:
        if activity['event_type'] == 'buy':
            stats['total_buys_count'] += 1
            stats['total_buy_amount_usd'] += round(float(activity['cost_usd']), 20) if activity['cost_usd'] else 0
            stats['total_buy_amount_token'] += round(float(activity['token_amount']), 20) if activity['token_amount'] else 0
            if not first_buy or (activity['timestamp'] <= first_buy['timestamp']):
                first_buy = activity

        else:
            stats['total_sales_count'] += 1
            stats['total_sell_amount_usd'] += round(float(activity['cost_usd']), 20) if activity['cost_usd'] else 0
            stats['total_sell_amount_token'] += round(float(activity['token_amount']), 20) if activity['token_amount'] else 0
            if not first_sell or (activity['timestamp'] <= first_sell['timestamp']):
                first_sell = activity

        if not last_activity or (activity['timestamp'] >= last_activity['timestamp']):
            last_activity = activity

    if first_buy:
        stats['first_buy_price_usd'] = round(float(first_buy['price_usd']), 20) if first_buy['price_usd'] else None
        stats['first_buy_timestamp'] = first_buy['timestamp']

    if first_sell:
        stats['first_sell_price_usd'] = round(float(first_sell['price_usd']), 20) if first_sell['price_usd'] else None
        stats['first_sell_timestamp'] = first_sell['timestamp']

    if first_buy and first_sell:
        stats['first_buy_sell_duration'] = first_sell['timestamp'] - first_buy['timestamp'] if (
                first_sell.get('timestamp') and first_buy.get('timestamp')) else None

    if stats['total_buys_count'] > 0:
        stats['total_profit_usd'] = stats['total_sell_amount_usd'] - stats['total_buy_amount_usd']
        stats['total_profit_percent'] = round(stats['total_profit_usd'] / stats['total_buy_amount_usd'] * 100, 2) if not \
            stats['total_buy_amount_usd'] == 0 else None

    if last_activity:
        stats['last_activity_timestamp'] = last_activity['timestamp']

    return stats
