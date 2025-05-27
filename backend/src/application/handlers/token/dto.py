from typing import Optional

from pydantic import BaseModel

from src.application.common.dto import PaginationResult


class TokenDTO(BaseModel):
    address: str
    name: Optional[str] = None
    symbol: Optional[str] = None
    uri: Optional[str] = None
    logo: Optional[str] = None
    created_on: Optional[str] = None

    class Config:
        from_attributes = True


class TokensDTO(BaseModel):
    tokens: list[TokenDTO]


class TokensPageDTO(TokensDTO):
    pagination: PaginationResult


class GetTokensFilters(BaseModel):
    pass
