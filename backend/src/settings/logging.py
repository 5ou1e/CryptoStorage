import logging
import logging.config
import os

log_dir = "./logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

CELERY_LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
        # 'file': {
        #     'level': 'DEBUG',
        #     'class': 'logging.FileHandler',
        #     'filename': 'celery_tasks.log',
        #     'formatter': 'verbose',
        # },
        "task_collect_sol_prices_file": {
            "level": "DEBUG",
            "class": "logging.FileHandler",
            "filename": "logs/task_collect_sol_prices.log",  # Укажите путь к файлу для логов этой задачи
            "formatter": "verbose",
        },
        "task_parse_tokens_metadata_file": {
            "level": "DEBUG",
            "class": "logging.FileHandler",
            "filename": "logs/task_parse_tokens_metadata.log",  # Укажите путь к файлу для логов этой задачи
            "formatter": "verbose",
        },
        "task_update_wallet_statistics": {
            "level": "DEBUG",
            "class": "logging.FileHandler",
            "filename": "logs/task_update_wallet_statistics.log",  # Укажите путь к файлу для логов этой задачи
            "formatter": "verbose",
        },
        "task_update_wallet_statistics_buy_price_gt_15k": {
            "level": "DEBUG",
            "class": "logging.FileHandler",
            "filename": "logs/task_update_wallet_statistics_buy_price_gt_15k.log",  # Укажите путь к файлу для логов этой задачи
            "formatter": "verbose",
        },
        "task_send_wallets_in_tg": {
            "level": "DEBUG",
            "class": "logging.FileHandler",
            "filename": "logs/task_send_wallets_in_tg.log",  # Укажите путь к файлу для логов этой задачи
            "formatter": "verbose",
        },
    },
    "loggers": {
        "tortoise": {
            "level": "WARNING",
            "handlers": ["console"],
            "propagate": False,
        },
        "celery": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "tasks.collect_sol_prices": {
            "handlers": [
                "console",
                "task_collect_sol_prices_file",
            ],
            "level": "DEBUG",
            "propagate": False,
        },
        "tasks.parse_tokens_metadata": {
            "handlers": [
                "console",
                "task_parse_tokens_metadata_file",
            ],
            "level": "DEBUG",
            "propagate": False,
        },
        "tasks.update_wallet_statistics": {
            "handlers": [
                "console",
                "task_update_wallet_statistics",
            ],
            "level": "INFO",
            "propagate": False,
        },
        "tasks.update_wallet_statistics_buy_price_gt_15k": {
            "handlers": [
                "console",
                "task_update_wallet_statistics_buy_price_gt_15k",
            ],
            "level": "INFO",
            "propagate": False,
        },
        "tasks.send_wallets_in_tg": {
            "handlers": [
                "console",
                "task_send_wallets_in_tg",
            ],
            "level": "INFO",
            "propagate": False,
        },
    },
}


def setup_celery_logging():
    logging.config.dictConfig(CELERY_LOGGING)


def setup_logging(level=logging.DEBUG):
    logging.basicConfig(
        format="%(asctime)s [%(levelname)s] %(message)s",
        level=level,
    )
