from pydantic import BaseModel, create_model, Field
from fastapi import Query
from typing import Optional


def generate_fields(prefix: str):
    return {
        f"{prefix}__total_token__lte": (
            Optional[int],
            Field(Query(None, description=f"({prefix.upper()}) Всего токенов ≤")),
        ),
        f"{prefix}__token_avg_buy_amount__gte": (
            Optional[float],
            Field(Query(None, description=f"({prefix.upper()}) Средний объем покупки ≥")),
        ),
        f"{prefix}__token_avg_buy_amount__lte": (
            Optional[float],
            Field(Query(None, description=f"({prefix.upper()}) Средний объем покупки ≤")),
        ),
        f"{prefix}__token_avg_profit_usd__gte": (
            Optional[float],
            Field(Query(None, description=f"({prefix.upper()}) Средний профит (USD) ≥")),
        ),
        f"{prefix}__token_avg_profit_usd__lte": (
            Optional[float],
            Field(Query(None, description=f"({prefix.upper()}) Средний профит (USD) ≤")),
        ),
    }


Filters = create_model(
    "Filters",
    **generate_fields("stats_all"),
    **generate_fields("stats_7d"),
    **generate_fields("stats_30d"),
    __base__=BaseModel,
)

filters = Filters(stats_all__total_token__lte=100, stats_7d__token_avg_profit_usd__gte=50.5)
print(filters.model_dump(exclude_unset=True))
