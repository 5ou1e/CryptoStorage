import asyncio
from asyncio import Semaphore
from datetime import timedelta

from asgiref.sync import sync_to_async
from celery import shared_task
from django.db.models import F, Q
from django.utils.timezone import now
from external_services.models import GmgnAPIClientConfig
from external_services.services.gmgn import GmgnAPIClient
from solana.models import Token, Wallet


@shared_task(bind=True)
def process_collect_wallets_from_token_transactions(self, batch_size=1000):

    asyncio.run(_process_collect_wallets_from_token_transactions_async(batch_size))

async def _process_collect_wallets_from_token_transactions_async(batch_size):
    five_minutes_ago = now() - timedelta(minutes=5) # Чекаем только если токен добавлен в БД более 5 минут назад
    # Асинхронно выбираем токены
    tokens = [token async for token in Token.objects.filter(
            Q(transactions_check_interval__isnull=False) &  # исключаем записи, где intervalcheck None
            (Q(last_transactions_check__lte=now() - F('transactions_check_interval')) | Q(
                last_transactions_check__isnull=True)) &
            Q(created_at__lte=five_minutes_ago)
            ).all().order_by('id')[:batch_size]
        ]
    print(f"Токенов необходимо чекнуть: {len(tokens)}")
    if tokens:
        # Если есть токены, обрабатываем их
        await collet_wallets_from_token_transactions(tokens)

        # Выполняем новый вызов задачи сразу
        process_collect_wallets_from_token_transactions.apply_async(countdown=1)
    else:
        # Если токенов нет, вызываем задачу через 1 минуту
        print("Нет токенов для обработки. Ожидаем 1 минуту")
        process_collect_wallets_from_token_transactions.apply_async(countdown=60)

async def collet_wallets_from_token_transactions(tokens):

    semaphore = Semaphore(10)

    settings = await GmgnAPIClientConfig.objects.afirst()
    client = GmgnAPIClient(
        proxy=settings.proxy,
        cookies=settings.cookies,
    )

    tasks = [process_token(semaphore, client, token) for token in tokens]
    results = await asyncio.gather(*tasks)
    collected_wallets = list(set([item for sublist in results for item in sublist]))
    # print(f"Собранные кошелки - {collected_wallets}")
    await bulk_import_wallets_to_db(collected_wallets)


    await client.close()


async def process_token(semaphore, client, token):
    """Получение новых транзакций токена и сбор адресов кошельков"""
    async with semaphore:
        collected_wallets = set()
        from_timestamp = int(token.last_transactions_check.timestamp()) if token.last_transactions_check else ""
        token_trades = await client.get_token_trades(token.address, from_timestamp=from_timestamp)
        await update_token(token, token_trades)

        for trade in token_trades:
            maker = trade.get("maker")
            if maker:
                collected_wallets.add(maker)
        collected_wallets = list(collected_wallets)

        return collected_wallets


async def update_token(token, token_trades):
    """Обновление времени чека и интервала до след.чека токена"""
    token_trades_count = len(token_trades)
    # print(f"По токену {token.address} собрано всего {token_trades_count} транз.")
    if token_trades_count == 0:
        token.transactions_check_interval = None
    # if token_trades_count >= 5000:
    #     token.transactions_check_interval = None

    token.last_transactions_check = now()
    await sync_to_async(token.save)()  # Сохраняем объект Token асинхронно


async def bulk_import_wallets_to_db(collected_wallets):
    """"Импорт собранных кошелков пачкой в бд"""
    wallets_to_create = []
    for wallet in collected_wallets:
        wallets_to_create.append(Wallet(
            address=wallet,
        ))
    if wallets_to_create:
        await Wallet.objects.abulk_create(wallets_to_create, batch_size=500, ignore_conflicts=True, )