import functools
import logging
import traceback


def task_logger(logger: logging.Logger):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                logger.info(f"Запуск задачи {func.__name__} с параметрами: args={args}, kwargs={kwargs}")
                result = func(*args, **kwargs)
                logger.info(f"Задача {func.__name__} успешно завершена!")
                return result
            except Exception as e:
                logger.error(f"Ошибка при выполнении задачи {func.__name__}: {e} | {traceback.format_exc()}")
                raise

        return wrapper

    return decorator
