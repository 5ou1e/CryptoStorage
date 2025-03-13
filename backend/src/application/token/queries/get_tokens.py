from src.application.common.dto import Pagination, PaginationResult
from src.application.interfaces.repositories.token import BaseTokenRepository
from src.application.token.dto import GetTokensFilters, TokenDTO, TokensPageDTO


class GetTokensHandler:
    def __init__(
        self,
        token_repository: BaseTokenRepository,
    ):
        self.token_repository = token_repository

    async def __call__(
        self,
        pagination: Pagination,
        filters: GetTokensFilters,
    ) -> TokensPageDTO:
        filter_by = filters.model_dump()
        tokens = await self.token_repository.get_page(
            pagination=pagination,
            # filter_by=filter_by,
        )
        total_count = await self.token_repository.get_count()
        tokens_dto = [TokenDTO.from_orm(token) for token in tokens]
        return TokensPageDTO(
            tokens=tokens_dto,
            pagination=PaginationResult.from_pagination(pagination, count=len(tokens_dto), total_count=total_count),
        )
