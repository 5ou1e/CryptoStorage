import math
from typing import TypeVar, Optional, List, Generic

from fastapi import Query
from pydantic import BaseModel, Field, field_validator


class Pagination(BaseModel):
    page: int = Query(1, ge=1, description="Номер страницы")
    page_size: int = Query(
        10,
        ge=1,
        le=100,
        description="Кол-во элементов на странице",
    )

    @property
    def limit_offset(self) -> tuple[int, int]:
        offset = (max(self.page, 1) - 1) * self.page_size
        limit = self.page_size
        return limit, offset


class PaginationResult(BaseModel):
    page: int
    page_size: int
    count: int
    total_count: int
    total_pages: int

    @classmethod
    def from_pagination(cls, pagination: Pagination, count: int, total_count: int) -> "PaginationResult":
        total_pages = math.ceil(total_count / pagination.page_size)
        return cls(
            page=pagination.page,
            page_size=pagination.page_size,
            count=count,
            total_count=total_count,
            total_pages=total_pages,
        )


SortingEnumType = TypeVar("SortingEnumType")


class BaseSorting(BaseModel, Generic[SortingEnumType]):
    order_by: Optional[List[SortingEnumType]] = Field(
        Query(None),
        description="Поля для сортировки",
    )

    @field_validator("order_by", mode="before")  # noqa
    @classmethod
    def remove_duplicates(cls, value):
        if value is None:
            return value
        return list(dict.fromkeys(value))  # Убираем дубликаты, сохраняя порядок
