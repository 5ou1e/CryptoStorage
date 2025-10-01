import logging.config
from functools import wraps
from pathlib import Path

from src.settings.config import config

LOGS_ROOT_DIR = Path(config.logs.root_dir)
LOGS_ROOT_DIR.mkdir(parents=True, exist_ok=True)  # Создание папки logs/

TASK_CONFIGS = {
    "collect_sol_prices_task": {
        "loggers": ["src"],  # включаем логирование для всех модулей проекта
        "handlers": {
            "file": {
                "class": "logging.FileHandler",
                "filename": f"{LOGS_ROOT_DIR}/collect_sol_prices_task.log",
                "level": "INFO",
                "formatter": "detailed",
            },
            "console": {
                "class": "logging.StreamHandler",
                "level": "INFO",
            },
        },
    },
    "parse_tokens_metadata_task": {
        "loggers": ["src"],  # включаем логирование для всех модулей проекта
        "handlers": {
            "file": {
                "class": "logging.FileHandler",
                "filename": f"{LOGS_ROOT_DIR}/parse_tokens_metadata_task.log",
                "level": "INFO",
                "formatter": "detailed",
            },
            "console": {
                "class": "logging.StreamHandler",
                "level": "INFO",
            },
        },
    },
    "send_wallets_in_tg_task": {
        "loggers": ["src"],  # включаем логирование для всех модулей проекта
        "handlers": {
            "file": {
                "class": "logging.FileHandler",
                "filename": f"{LOGS_ROOT_DIR}/send_wallets_in_tg_task.log",
                "level": "INFO",
                "formatter": "detailed",
            },
            "console": {
                "class": "logging.StreamHandler",
                "level": "INFO",
            },
        },
    },
    "update_wallet_statistics_task": {
        "loggers": ["src"],  # включаем логирование для всех модулей проекта
        "handlers": {
            "file": {
                "class": "logging.FileHandler",
                "filename": f"{LOGS_ROOT_DIR}/update_wallet_statistics_task.log",
                "level": "INFO",
                "formatter": "detailed",
            },
            "console": {
                "class": "logging.StreamHandler",
                "level": "INFO",
            },
        },
    },
    "update_single_wallet_statistics_task": {
        "loggers": ["src"],  # включаем логирование для всех модулей проекта
        "handlers": {
            "file": {
                "class": "logging.FileHandler",
                "filename": f"{LOGS_ROOT_DIR}/update_single_wallet_statistics_task.log",
                "level": "INFO",
                "formatter": "detailed",
            },
            "console": {
                "class": "logging.StreamHandler",
                "level": "INFO",
            },
        },
    },
    "update_wallet_statistics_buy_price_gt_15k_task": {
        "loggers": ["src"],  # включаем логирование для всех модулей проекта
        "handlers": {
            "file": {
                "class": "logging.FileHandler",
                "filename": f"{LOGS_ROOT_DIR}/update_wallet_statistics_buy_price_gt_15k_task.log",
                "level": "INFO",
                "formatter": "detailed",
            },
            "console": {
                "class": "logging.StreamHandler",
                "level": "INFO",
            },
        },
    },
    "update_wallet_statistics_copyable_task": {
        "loggers": ["src"],  # включаем логирование для всех модулей проекта
        "handlers": {
            "file": {
                "class": "logging.FileHandler",
                "filename": f"{LOGS_ROOT_DIR}/update_wallet_statistics_copyable_task.log",
                "level": "INFO",
                "formatter": "detailed",
            },
            "console": {
                "class": "logging.StreamHandler",
                "level": "INFO",
            },
        },
    },
    "swaps_loader_delays_alerter_task": {
        "loggers": ["src"],  # включаем логирование для всех модулей проекта
        "handlers": {
            "file": {
                "class": "logging.FileHandler",
                "filename": f"{LOGS_ROOT_DIR}/swaps_loader_delays_alerter_task.log",
                "level": "INFO",
                "formatter": "detailed",
            },
            "console": {
                "class": "logging.StreamHandler",
                "level": "INFO",
            },
        },
    },

}


def setup_task_logging(task_name: str):
    cfg = TASK_CONFIGS.get(task_name)
    if not cfg:
        return

    handlers_config = {}
    handler_names = []

    for name, handler in cfg["handlers"].items():
        handler_name = f"{task_name}_{name}"
        handler_names.append(handler_name)
        handlers_config[handler_name] = handler
    print(handler_names)
    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "detailed": {"format": "[%(asctime)s] %(levelname)s %(name)s: %(message)s"},
            },
            "handlers": handlers_config,
            "loggers": {
                logger_name: {
                    "handlers": handler_names,
                    "level": "DEBUG",
                    "propagate": False,
                }
                for logger_name in cfg["loggers"]
            },
        }
    )
