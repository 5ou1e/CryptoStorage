from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine as sa_create_async_engine

from src.settings import config


engine = sa_create_async_engine(
    config.db.url_sa,
    echo=False,
    pool_size=config.db.min_size,
    max_overflow=config.db.max_size,
)


AsyncSessionMaker = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    autoflush=False,
)
