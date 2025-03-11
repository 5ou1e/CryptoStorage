from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.settings import config

engine = create_async_engine(
    config.db.url_sa,
    echo=True,
    pool_size=config.db.min_size,  # Минимальное количество соединений в пуле
    max_overflow=config.db.max_size,  # Максимальное количество соединений, которые могут быть "переполнены"
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    autoflush=False,
)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
        # await session.commit()
