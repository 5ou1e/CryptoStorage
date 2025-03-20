from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseConfig(BaseSettings):
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


class DjangoConfig(BaseConfig):
    model_config = SettingsConfigDict(
        env_prefix="DJANGO_",  # Указываем префикс для переменных окружения
    )
    secret_key: str = Field()
    debug: bool = Field(True)
    allowed_hosts: List[str] = Field(["*"])
    csrf_trusted_origins: List[str] = Field()
    time_zone: str = Field('Europe/Moscow')


class DjangoUnfoldConfig(BaseConfig):
    model_config = SettingsConfigDict(
        env_prefix="DJANGO_UNFOLD_",  # Указываем префикс для переменных окружения
    )
    site_title: str = Field("CryptoStorage Admin-panel")
    site_header: str = Field("CryptoStorage")


class DatabaseConfig(BaseConfig):
    model_config = SettingsConfigDict(
        env_prefix="DB_",  # Указываем префикс для переменных окружения
    )
    user: str = Field()
    password: str = Field()
    host: str = Field()
    port: int = Field()
    name: str = Field()


class Config(BaseSettings):
    django: DjangoConfig = DjangoConfig()
    django_unfold: DjangoUnfoldConfig = DjangoUnfoldConfig()
    db: DatabaseConfig = DatabaseConfig()


config = Config()
