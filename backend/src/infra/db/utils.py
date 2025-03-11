import logging
import textwrap
from datetime import datetime
from typing import Any

from tortoise import Model, Tortoise

logger = logging.getLogger(__name__)


async def bulk_update_records_query(
    model_cls: Model,
    objects: list,
    fields_to_update: list,
    id_column: Any | None = None,
):
    """
    Универсальная функция для массового обновления записей.
    Данная реализация использует подход с VALUES IN вместо CASE WHEN
    """
    # Получаем имя таблицы из модели
    table_name = model_cls._meta.db_table
    if id_column is None:
        id_column = model_cls._meta.db_pk_column
    if id_column not in fields_to_update:
        fields_to_update.append(id_column)

    # Преобразуем объекты в словари
    updates = []

    for obj in objects:
        print(type(obj))
        d = {}
        for field in fields_to_update:
            # Получаем тип поля из модели через _meta.fields_map
            field_info = model_cls._meta.fields_map.get(field)
            if field_info:
                field_type = field_info.__class__.__name__.lower()
            else:
                raise ValueError(f"Ошибка: В модели {model_cls} не задано поле {field}")
            value = getattr(obj, field)
            d[field] = convert_to_db_value(value, field_type, field_info)
        updates.append(d)

    # Вычисляем все уникальные столбцы
    all_columns = set().union(*(update.keys() for update in updates))
    all_columns.discard(id_column)  # Удаляем столбец ID, он не обновляется напрямую

    # Формируем строку столбцов
    columns_str = ", ".join([id_column] + list(all_columns))

    # Формируем строку VALUES
    values = []
    for update in updates:
        row = [update.get(id_column)] + [update.get(col, None) for col in all_columns]
        values.append(f"({', '.join(row)})")
    values_str = ", ".join(values)

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
    # logger.error(query[:2000])
    return await Tortoise.get_connection("default").execute_query(query)


def convert_to_db_value(value, field_type=None, field_info=None):
    if value is None:
        value = "NULL"
    if field_type in [
        "decimalfield",
        "mydecimalfield",
    ]:
        return f"CAST({value} AS DECIMAL({field_info.max_digits},{field_info.decimal_places}))"
    elif field_type == "floatfield":
        return f"CAST({value} AS double precision)"
    elif field_type == "bigintfield":
        return f"CAST({value} AS bigint)"
    elif field_type == "intfield":
        return f"CAST({value} AS integer)"
    elif field_type == "booleanfield":
        return "TRUE" if value else "FALSE"
    elif field_type == "datetimefield":
        if not value == "NULL":
            value = value.isoformat()
            return f"CAST('{value}' AS timestamp with time zone)"
        else:
            return f"CAST({value} AS timestamp with time zone)"
    elif field_type == "uuidfield":
        return f"CAST('{value}' AS uuid)"
    elif field_type == "charfield":
        return f"'{value}'"
    return str(value)  # Если не указан тип поля, просто возвращаем строку
