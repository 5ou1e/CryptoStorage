import logging
from datetime import datetime
from typing import Any, List

from tortoise import Model, Tortoise
from pypika import Query, Table, Field, Parameter

from src.infra.db.models.tortoise import Wallet

logger = logging.getLogger(__name__)


def bulk_update_records_query(
    model_cls: Model,
    objects: list,
    fields_to_update: list,
    id_column: Any | None = None,
):
    """
    Универсальная функция для массового обновления записей.
    Данная реализация использует PyPika для построения SQL-запроса
    с учетом типов данных полей.
    """
    # Получаем имя таблицы из модели
    table_name = model_cls._meta.db_table
    table = Table(table_name)

    if id_column is None:
        id_column = model_cls._meta.db_pk_column
    if id_column not in fields_to_update:
        fields_to_update.append(id_column)

    # Преобразуем объекты в словари
    updates = []

    for obj in objects:
        d = {}
        for field in fields_to_update:
            # Получаем тип поля из модели через _meta.fields_map
            field_info = model_cls._meta.fields_map.get(field)
            if field_info:
                field_type = field_info.__class__.__name__.lower()
            else:
                raise ValueError(f"Ошибка: В модели {model_cls} не задано поле {field}")
            value = getattr(obj, field)
            d[field] = value  # Храним значения напрямую, не конвертируя их

        updates.append(d)

    # Формируем строки VALUES
    values = []
    for update in updates:
        row = [update.get(id_column)] + [update.get(col, None) for col in fields_to_update if col != id_column]
        values.append(row)

    # Формируем SQL-запрос с использованием PyPika
    query = Query.from_(Query.from_("(VALUES (CAST(:id AS UUID), CAST(:updated_at AS TIMESTAMPTZ)))").as_("v")).update(table).where(table.id == Field("v.id"))
    print(query.get_sql())


    # Добавляем обновления для каждого поля
    set_clause = []
    for col in fields_to_update:
        v_col = Field(f"v.{col}")
        if col != id_column:
            query = query.set(Field(col), v_col)  # Передаем параметры в правильной форме

    query.from_(Query.from_("(VALUES (CAST(:id AS UUID), CAST(:updated_at AS TIMESTAMPTZ)))").as_("v"))
    print(query.get_sql())
    logger.debug(f"Generated SQL query: {query.get_sql()}")


wallets = [Wallet(address='1231231')]

bulk_update_records_query(Wallet, wallets, fields_to_update=['updated_at'])
#
# wallet = Table('wallet')
# # Здесь нам нужно сгенерировать подзапрос для VALUES, что не тривиально.
# # PyPika не имеет прямой поддержки для генерации массивов плейсхолдеров,
# # так что, возможно, вам придётся комбинировать ручное формирование части запроса с PyPika.
#
# # Например, для одной строки:
# v_id = Field("v.id")
# v_updated_at = Field("v.updated_at")
#
# q = Query.update(wallet).set(wallet.updated_at, v_updated_at).from_(
#     Query.from_("(VALUES (CAST(:id AS UUID), CAST(:updated_at AS TIMESTAMPTZ)))").as_("v")
# ).where(wallet.id == Field("v.id"))
#
# print(q.get_sql())

q = Query.into("my_table").columns(
    "col_1",
    "col_2"
).insert(Parameter(":1")).from_(Query.from_("(VALUES (CAST(:id AS UUID), CAST(:updated_at AS TIMESTAMPTZ)))").as_("v"))
print(q.get_sql())
