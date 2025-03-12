import asyncio
from datetime import timedelta

from celery import shared_task
from external_services.services.gmgn import GmgnAPIClient
from solana.models import Token


@shared_task(bind=True, ignore_result=False)
def process_collect_new_tokens(self):
    """
    Задача для парсинга новых токенов с GMGN.
    """
    return asyncio.run(_process_collect_new_tokens_async())


async def _process_collect_new_tokens_async():
    settings = await GmgnAPIClientConfig.objects.afirst()
    client = GmgnAPIClient(
        proxy=settings.proxy,
        cookies=settings.cookies,
    )
    try:
        new_pools = await client.get_new_pools()
        await import_new_tokens_to_db(new_pools)
    except Exception as e:
        raise e
    finally:
        await client.close()
    return 'OK'

async def import_new_tokens_to_db(new_pools):
    tokens_to_create = []
    for new in new_pools:
        address = new.get('base_address')
        token_info = new.get('base_token_info')
        if not address or not token_info:
            continue
        tokens_to_create.append(Token(
            address=address,
            name=token_info.get('name'),
            symbol=token_info.get('symbol'),
            decimals=None,
            logo=token_info['logo'][:500] if token_info.get('logo') else None,
            price=token_info.get('price'),
            total_supply=token_info.get('total_supply'),
            transactions_check_interval=timedelta(days=1),
        ))
    if tokens_to_create:
        await Token.objects.abulk_create(tokens_to_create, ignore_conflicts=True,)