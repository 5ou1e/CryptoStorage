from dotenv import load_dotenv
from pydantic import BaseModel
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)

load_dotenv()


class DatabaseConfig(BaseModel):
    user: str
    password: str
    host: str
    port: int
    name: str
    min_size: int = 10
    max_size: int = 200
    max_queries: int = 1000

    @property
    def url_tortoise(self) -> str:
        # url for Tortoise-ORM
        return f"asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}?minsize={self.min_size}&maxsize={self.max_size}&max_queries={self.max_queries}"

    @property
    def url_sa(self) -> str:
        # URL для SQLAlchemy (asyncpg)
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"


class CORSConfig(BaseModel):
    allowed_hosts: list[str]


class AccessTokenConfig(BaseModel):
    secret_key: str
    algorithm: str
    expire_minutes: int = 30


class CeleryTasksConfig(BaseModel):
    collect_sol_prices_task_interval: int = 60  # интервал запуска сбора цен Соланы
    parse_tokens_metadata_task: int = 60  # интервал запуска парсинга метаданных токена в секундах
    send_wallets_in_tg_task_interval: int = 3600  # интервал отправки тг-алертов с кошельками в секундах
    update_wallet_statistics_buy_price_gt_15k_task_interval: int = (
        3600  # интервал обновления walletstatsgt15k в секундах
    )


class CeleryConfig(BaseModel):
    broker_url: str
    result_backend: str
    tasks: CeleryTasksConfig = CeleryTasksConfig()


class SolanaConfig(BaseModel):
    token_address: str
    rpc_node_url: str


class TelegramConfig(BaseModel):
    bot_token: str
    wallet_alerts_channel_id: str


class ApiV1Config(BaseModel):
    prefix: str = "/v1"


class ApiConfig(BaseModel):
    prefix: str = "/api"
    v1: ApiV1Config = ApiV1Config()


class Config(BaseSettings):
    model_config = SettingsConfigDict(
        case_sensitive=False,
        env_nested_delimiter="__",
        env_prefix="BACKEND__",
    )

    api: ApiConfig
    access_token: AccessTokenConfig
    db: DatabaseConfig
    cors: CORSConfig
    celery: CeleryConfig
    solana: SolanaConfig
    telegram: TelegramConfig


config: Config = Config()
