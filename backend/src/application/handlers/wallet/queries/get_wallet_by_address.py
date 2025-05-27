from src.application.common.interfaces.readers import WalletReaderInterface
from src.application.handlers.wallet.dto import WalletDTO


class GetWalletByAddressHandler:
    def __init__(
        self,
        wallet_reader: WalletReaderInterface,
    ) -> None:
        self._reader = wallet_reader

    async def __call__(self, address: str) -> WalletDTO:
        return await self._reader.get_wallet_by_address(address)
