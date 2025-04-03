from sqlalchemy import select
from sqlalchemy.orm import joinedload, contains_eager


from src.application.common.dto import Pagination, PaginationResult
from src.application.interfaces.readers import WalletReaderInterface
from src.application.wallet.dto import WalletDTO, WalletsPageDTO, GetWalletsFilters
from src.application.wallet.dto.wallet import GetWalletsSorting
from src.application.wallet.dto.wallet_activity import (
    WalletActivitiesPageDTO,
    WalletActivityDTO,
    GetWalletActivitiesSorting,
    GetWalletActivitiesFilters,
)
from src.application.wallet.dto.wallet_token import (
    WalletTokenDTO,
    WalletTokensPageDTO,
    GetWalletTokensFilters,
    GetWalletTokensSorting,
)
from src.application.wallet.exceptions import WalletNotFoundException
from src.infra.db.sqlalchemy.models import (
    Swap,
    Wallet,
    WalletToken,
    WalletStatistic30d,
    WalletStatisticAll,
    WalletStatistic7d,
    Token,
)
from src.infra.db.sqlalchemy.readers.generic_reader import SQLAlchemyBaseReader


class SQLAlchemyWalletReader(SQLAlchemyBaseReader, WalletReaderInterface):

    async def get_wallet_by_address(self, address: str) -> WalletDTO:
        query = select(Wallet).where(Wallet.address == address)
        query = query.options(
            joinedload(Wallet.stats_7d),
            joinedload(Wallet.stats_30d),
            joinedload(Wallet.stats_all),
        )
        result = await self._session.scalars(query)
        wallet = result.first()
        if not wallet:
            raise WalletNotFoundException(address)
        return WalletDTO.from_orm(wallet)

    async def get_wallets(
        self,
        pagination: Pagination,
        filters: GetWalletsFilters,
        sorting: GetWalletsSorting
    ) -> WalletsPageDTO:
        query = select(Wallet)
        query = (
            query.join(WalletStatistic30d)
            .join(WalletStatisticAll)
            .join(WalletStatistic7d)
            .options(
                contains_eager(Wallet.stats_7d), contains_eager(Wallet.stats_30d), contains_eager(Wallet.stats_all)
            )
        )

        limit, offset = pagination.limit_offset
        query, count_query = self._apply_filters_sorting_limit_offset(query, Wallet, filters, sorting, limit, offset)

        instances = await self._session.scalars(query)
        wallets = [WalletDTO.from_orm(instance) for instance in instances]
        count = len(wallets)

        total_count = await self._get_count(count_query)

        return WalletsPageDTO(
            wallets=wallets,
            pagination=PaginationResult.from_pagination(pagination, count=count, total_count=total_count),
        )

    async def get_wallet_activities(
        self,
        address: str,
        pagination: Pagination,
        filters: GetWalletActivitiesFilters,
        sorting: GetWalletActivitiesSorting,
    ) -> WalletActivitiesPageDTO:
        wallet_id = await self._get_wallet_id_by_address(address)
        if not wallet_id:
            raise WalletNotFoundException(address)

        query = select(Swap).where(Swap.wallet_id == wallet_id)
        query = query.join(Token).options(contains_eager(Swap.token))

        limit, offset = pagination.limit_offset
        query, count_query = self._apply_filters_sorting_limit_offset(query, Swap, filters, sorting, limit, offset)

        instances = await self._session.scalars(query)
        activities = [WalletActivityDTO.from_orm(instance) for instance in instances]
        count = len(activities)
        total_count = await self._get_count(count_query)

        return WalletActivitiesPageDTO(
            activities=activities,
            pagination=PaginationResult.from_pagination(pagination, count=count, total_count=total_count),
        )

    async def get_wallet_tokens(
        self,
        address: str,
        pagination: Pagination,
        filters: GetWalletTokensFilters,
        sorting: GetWalletTokensSorting,
    ) -> WalletTokensPageDTO:
        wallet_id = await self._get_wallet_id_by_address(address)
        if not wallet_id:
            raise WalletNotFoundException(address)

        query = select(WalletToken).where(WalletToken.wallet_id == wallet_id)
        query = (
            query
            .join(Token)
            # .join(Wallet)
            .options(
                contains_eager(WalletToken.token),
                # contains_eager(WalletToken.wallet)
            )
        )

        limit, offset = pagination.limit_offset
        query, count_query = self._apply_filters_sorting_limit_offset(query, WalletToken, filters, sorting, limit, offset)

        instances = await self._session.scalars(query)
        wallet_tokens = [WalletTokenDTO.from_orm(instance) for instance in instances]
        count = len(wallet_tokens)
        total_count = await self._get_count(count_query)

        return WalletTokensPageDTO(
            wallet_tokens=wallet_tokens,
            pagination=PaginationResult.from_pagination(pagination, count=count, total_count=total_count),
        )

    async def _get_wallet_id_by_address(self, address: str) -> int | None:
        stmt = select(Wallet.id).where(Wallet.address == address)
        result = await self._session.scalars(stmt)
        return result.first()
