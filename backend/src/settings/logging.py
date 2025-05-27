import logging
import logging.config
from pathlib import Path

from src.settings.config import config

LOGS_ROOT_DIR = Path(config.logs.root_dir)
LOGS_ROOT_DIR.mkdir(parents=True, exist_ok=True)  # Создание папки logs/


def setup_logging(level=logging.DEBUG):
    logging.basicConfig(
        format="%(asctime)s [%(levelname)s] %(message)s",
        level=level,
    )
