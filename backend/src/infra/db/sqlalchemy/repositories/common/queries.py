import textwrap
from typing import Any, List

from sqlalchemy import (
    DECIMAL,
    Boolean,
    Date,
    DateTime,
    Float,
    Integer,
    String,
    Uuid,
    case,
    cast,
    extract,
    func,
    or_,
)
from sqlalchemy.dialects.postgresql import insert
from src.infra.db.sqlalchemy.models import WalletToken


def get_bulk_update_or_create_wallet_token_with_merge_stmt():
    stmt = insert(WalletToken)
    stmt = stmt.on_conflict_do_update(
        index_elements=["wallet_id", "token_id"],
        set_={
            "total_buys_count": WalletToken.total_buys_count
            + stmt.excluded.total_buys_count,
            "total_buy_amount_usd": WalletToken.total_buy_amount_usd
            + stmt.excluded.total_buy_amount_usd,
            "total_buy_amount_token": WalletToken.total_buy_amount_token
            + stmt.excluded.total_buy_amount_token,
            "first_buy_price_usd": case(
                (
                    (
                        or_(
                            WalletToken.first_buy_timestamp.is_(None),
                            stmt.excluded.first_buy_timestamp
                            < WalletToken.first_buy_timestamp,
                        ),
                        stmt.excluded.first_buy_price_usd,
                    )
                ),
                else_=WalletToken.first_buy_price_usd,
            ),
            "first_buy_timestamp": func.least(
                WalletToken.first_buy_timestamp, stmt.excluded.first_buy_timestamp
            ),
            "total_sales_count": WalletToken.total_sales_count
            + stmt.excluded.total_sales_count,
            "total_sell_amount_usd": WalletToken.total_sell_amount_usd
            + stmt.excluded.total_sell_amount_usd,
            "total_sell_amount_token": WalletToken.total_sell_amount_token
            + stmt.excluded.total_sell_amount_token,
            "first_sell_price_usd": func.coalesce(
                WalletToken.first_sell_price_usd, stmt.excluded.first_sell_price_usd
            ),
            "first_sell_timestamp": case(
                (
                    (
                        or_(
                            WalletToken.first_sell_timestamp.is_(None),
                            stmt.excluded.first_sell_timestamp
                            < WalletToken.first_sell_timestamp,
                        ),
                        stmt.excluded.first_sell_timestamp,
                    )
                ),
                else_=WalletToken.first_sell_timestamp,
            ),
            "last_activity_timestamp": func.greatest(
                WalletToken.last_activity_timestamp,
                stmt.excluded.last_activity_timestamp,
            ),
            "total_profit_usd": WalletToken.total_profit_usd
            + stmt.excluded.total_profit_usd,
            "total_profit_percent": case(
                (
                    WalletToken.total_buy_amount_usd
                    + stmt.excluded.total_buy_amount_usd
                    > 0,
                    (
                        (
                            WalletToken.total_sell_amount_usd
                            + stmt.excluded.total_sell_amount_usd
                        )
                        - (
                            WalletToken.total_buy_amount_usd
                            + stmt.excluded.total_buy_amount_usd
                        )
                    )
                    / (
                        WalletToken.total_buy_amount_usd
                        + stmt.excluded.total_buy_amount_usd
                    )
                    * 100,
                ),
                else_=None,
            ),
            "first_buy_sell_duration": case(
                (
                    (
                        func.least(
                            WalletToken.first_buy_timestamp,
                            stmt.excluded.first_buy_timestamp,
                        ).isnot(None)
                        & func.least(
                            WalletToken.first_sell_timestamp,
                            stmt.excluded.first_sell_timestamp,
                        ).isnot(None)
                        & (
                            func.least(
                                WalletToken.first_sell_timestamp,
                                stmt.excluded.first_sell_timestamp,
                            )
                            - func.least(
                                WalletToken.first_buy_timestamp,
                                stmt.excluded.first_buy_timestamp,
                            )
                            >= 0
                        )
                    ),
                    cast(
                        extract(
                            "epoch",
                            func.least(
                                WalletToken.first_sell_timestamp,
                                stmt.excluded.first_sell_timestamp,
                            )
                            - func.least(
                                WalletToken.first_buy_timestamp,
                                stmt.excluded.first_buy_timestamp,
                            ),
                        ),
                        Integer,
                    ),
                ),
                else_=None,
            ),
            "total_swaps_from_txs_with_mt_3_swappers": WalletToken.total_swaps_from_txs_with_mt_3_swappers
            + stmt.excluded.total_swaps_from_txs_with_mt_3_swappers,
            "total_swaps_from_arbitrage_swap_events": WalletToken.total_swaps_from_arbitrage_swap_events
            + stmt.excluded.total_swaps_from_arbitrage_swap_events,
            "updated_at": func.now(),
        },
    )
    # print(stmt.compile())
    return stmt


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


def build_bulk_update_query(
    model_cls: Any,
    values: List[Any],
    fields_to_update: set[str],
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
        fields_to_update.add(id_column)

    # Преобразуем объекты в словари
    updates = []

    for obj in values:
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
