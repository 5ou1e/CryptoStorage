from sqlalchemy import select

from src.application.common.dto import Pagination, PaginationResult
from src.application.common.exceptions import TokenNotFoundException
from src.application.common.interfaces.readers import TokenReaderInterface
from src.application.handlers.token.dto import TokenDTO, TokensPageDTO
from src.infra.db.sqlalchemy.models import Token
from src.infra.db.sqlalchemy.readers.generic_reader import SQLAlchemyBaseReader


class SQLAlchemyTokenReader(SQLAlchemyBaseReader, TokenReaderInterface):

    async def get_tokens(self, pagination: Pagination) -> TokensPageDTO:
        limit, offset = pagination.limit_offset

        query = query_for_count = select(Token)
        query = query.offset(offset).limit(limit)

        instances = await self._session.scalars(query)
        tokens = [TokenDTO.from_orm(instance) for instance in instances]
        count = len(tokens)

        total_count = await self._get_count(query_for_count)

        return TokensPageDTO(
            tokens=tokens,
            pagination=PaginationResult.from_pagination(pagination, count=count, total_count=total_count),
        )

    async def get_token_by_address(self, address: str) -> TokenDTO:
        stmt = select(Token).where(Token.address == address)
        instance = (await self._session.scalars(stmt)).first()
        if not instance:
            raise TokenNotFoundException(address)
        return TokenDTO.from_orm(instance)
