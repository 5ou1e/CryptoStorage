from datetime import datetime, timedelta
from typing import Optional, Union


def format_datetime(value: datetime):
    if value is None:
        return None
    return value.strftime("%d-%m-%Y %H:%M:%S")


def format_duration(
    duration: Union[timedelta, int],
    none_value="-",
):
    if duration is None:
        return none_value
    if isinstance(duration, int):
        duration = timedelta(seconds=duration)
    # Проверка на отрицательное значение
    if duration.total_seconds() < 0:
        return f"-{format_duration(abs(duration), none_value)}"  # Рекурсивно вызываем для абсолютного значения
    # Проверяем дни, часы, минуты, секунды
    if duration.days > 0:
        return f"{duration.days}д"
    elif duration.seconds >= 3600:
        hours = duration.seconds // 3600
        return f"{hours}ч"
    elif duration.seconds >= 60:
        minutes = duration.seconds // 60
        return f"{minutes}м"
    else:
        return f"{duration.seconds}с"
