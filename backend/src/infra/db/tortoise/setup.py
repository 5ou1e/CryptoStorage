from fastapi import FastAPI
from src.settings import config
from tortoise import Tortoise
from tortoise.contrib.fastapi import register_tortoise

TORTOISE_ORM = {
    "connections": {"default": config.db.url_tortoise},
    "apps": {
        "models": {
            "models": [
                "src.infra.db.tortoise.models",
                "aerich.models",
            ],
            "default_connection": "default",
        },
    },
    "use_tz": True,
    "timezone": "UTC",
}


def register_db(app: FastAPI) -> None:
    register_tortoise(
        app,
        db_url=config.db.url_tortoise,
        modules={"models": ["src.infra.db.tortoise.models"]},
        generate_schemas=False,
        add_exception_handlers=True,
    )


async def init_db_async():
    await Tortoise.init(config=TORTOISE_ORM)
