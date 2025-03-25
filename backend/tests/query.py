import textwrap
from typing import Any, List

from sqlalchemy import DECIMAL, Boolean, Date, DateTime, Float, Integer, String, Uuid


def cast_value(value, field_type):
    """
    Функция для кастования значения в строку SQL в зависимости от типа колонки
    """
    if value is None:
        value = "NULL"

    # Кастуем в зависимости от типа
    if isinstance(field_type, Integer):
        return f"CAST({value} AS INTEGER)"
    elif isinstance(field_type, String):
        return f"'{value}'"  # Вставляем строковое значение
    elif isinstance(field_type, DateTime):
        if not value == "NULL":
            value = value.isoformat()
            return f"CAST('{value}' AS timestamp with time zone)"
        else:
            return f"CAST({value} AS timestamp with time zone)"
    elif isinstance(field_type, Float):
        return f"CAST({value} AS DOUBLE PRECISION)"
    elif isinstance(field_type, Boolean):
        return "TRUE" if value else "FALSE"
    elif isinstance(field_type, DECIMAL):
        return f"CAST({value} AS DECIMAL({field_type.precision},{field_type.scale}))"
    elif isinstance(field_type, Date):
        return f"CAST('{value.isoformat()}' AS DATE)"
    elif isinstance(field_type, Uuid):
        return f"CAST('{value}' AS UUID)"
    else:
        raise ValueError(f"Неизвестный тип для кастования: {field_type}")


async def get_bulk_update_records_query(
    model_cls: Any,
    objects: List[Any],
    fields_to_update: List[str],
    id_column: str = None,
):
    """
    Универсальная функция для массового обновления записей.
    Данная реализация использует подход с VALUES IN вместо CASE WHEN.
    """
    # Получаем имя таблицы из модели
    table_name = model_cls.__tablename__
    if id_column is None:
        id_column = model_cls.__mapper__.primary_key[0].name
    if not id_column:
        raise ValueError(f"Ошибка - у модели {model_cls} не задан PK")
    if id_column not in fields_to_update:
        fields_to_update.append(id_column)

    # Преобразуем объекты в словари
    updates = []

    for obj in objects:
        d = {}
        for field in fields_to_update:
            field_info = model_cls.__mapper__.columns.get(field)
            field_type = field_info.type
            # Получаем значение и применяем кастование
            # value = getattr(obj, field)
            value = obj[field]
            d[field] = cast_value(value, field_type)
        updates.append(d)

    # Формируем строку столбцов и значений
    all_columns = set().union(*(update.keys() for update in updates))
    all_columns.discard(id_column)

    columns_str = ", ".join([id_column] + list(all_columns))
    values_str = ", ".join(
        [
            f"({', '.join([update.get(id_column)] + [update.get(col, 'NULL') for col in all_columns])})"
            for update in updates
        ]
    )

    # Формируем строку SET для SQL
    set_clause = ", ".join([f"{col} = v.{col}" for col in all_columns])

    # Генерируем запрос
    query = textwrap.dedent(
        f"""\
        UPDATE {table_name}\
        SET {set_clause}\
        FROM (VALUES {values_str}) AS v({columns_str})\
        WHERE {table_name}.{id_column} = v.{id_column};
    """
    )
    return query
