import logging

# Создаем основной логгер
logger = logging.getLogger(__name__)

# Устанавливаем общий уровень логирования
logger.setLevel(logging.DEBUG)

# Формат для логов
log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Форматтер для логов
formatter = logging.Formatter(log_format, datefmt="%Y-%m-%d %H:%M:%S")

# Создаем обработчик для записи в файл
file_handler = logging.FileHandler("swaps_parser.log", encoding="utf-8")
file_handler.setLevel(logging.INFO)  # Уровень логирования для файла
file_handler.setFormatter(formatter)

# Создаем обработчик для вывода в консоль
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)  # Уровень логирования для консоли
console_handler.setFormatter(formatter)

# Добавляем обработчики в логгер
logger.addHandler(file_handler)
logger.addHandler(console_handler)
