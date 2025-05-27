import logging
import os
from pathlib import Path

# Убедимся, что директория для логов существует
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

# Формат логов
log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
formatter = logging.Formatter(log_format, datefmt="%Y-%m-%d %H:%M:%S")

# Обработчик для файла
file_handler = logging.FileHandler(LOG_DIR / "swaps_loader.log", encoding="utf-8")
file_handler.setLevel(logging.DEBUG)  # Логировать всё
file_handler.setFormatter(formatter)

# Обработчик для консоли
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)

# Получаем корневой логгер (именно он охватывает ВСЕ логи)
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)  # Общий уровень
root_logger.addHandler(file_handler)
root_logger.addHandler(console_handler)
