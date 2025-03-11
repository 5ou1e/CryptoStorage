from src.application.interfaces.repositories.wallet import (
    BaseWalletRepository,
)
from src.application.wallet.dto import (
    WalletDetailedDTO,
    WalletDTO,
)
from src.application.wallet.exceptions import (
    WalletNotFoundException,
)


class GetWalletByAddressHandler:
    def __init__(
        self,
        wallet_repository: BaseWalletRepository,
    ) -> None:
        self._wallet_repository = wallet_repository

    async def __call__(self, address: str) -> WalletDetailedDTO:
        wallet = await self._wallet_repository.get_by_address(address=address)
        # wallet = await self._wallet_repository.get_by_address_with_details_and_stats(address=address)
        if not wallet:
            raise WalletNotFoundException(address)
        return WalletDTO.from_orm(wallet)
