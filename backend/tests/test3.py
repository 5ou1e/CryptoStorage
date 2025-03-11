import asyncio
from dataclasses import asdict, dataclass

from sqlalchemy import select

from src.infra.db.models.tortoise import WalletStatistic30d
from src.infra.db.models.tortoise import Wallet
from src.infra.db.models.tortoise import Token
from src.infra.db.models.tortoise.wallet import WalletStatistic
from src.infra.db.repositories.tortoise import TortoiseTokenRepository
from src.infra.db.setup import get_db_session
from src.infra.db.setup_tortoise import init_db_async


async def main():
    await init_db_async()
    wallets = await Wallet.all()
    stats_list = []
    for wallet in wallets:
        stats = WalletStatistic30d(
            wallet_id=wallet.id,
        )
        stats_list.append(stats)
    await WalletStatistic30d.bulk_create(
        stats_list,
        batch_size=10000,
        ignore_conflicts=True
    )


asyncio.run(main())
