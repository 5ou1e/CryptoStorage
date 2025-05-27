from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class RelatedWalletDTO(BaseModel):
    address: str
    last_activity_timestamp: Optional[datetime] = None
    last_intersected_tokens_trade_timestamp: Optional[datetime] = None
    total_profit_usd_30d: Optional[float] = (None,)
    total_profit_multiplier_30d: Optional[float] = (None,)
    total_token_count: Optional[int] = None
    intersected_tokens_count: Optional[int] = None
    intersected_tokens_percent: Optional[float] = None
    mixed_count: Optional[int] = None
    same_count: Optional[int] = None
    after_count: Optional[int] = None
    before_count: Optional[int] = None
    color: Optional[str] = None


class SimilarWalletDTO(RelatedWalletDTO):
    pass


class CopyingWalletDTO(RelatedWalletDTO):
    pass


class CopiedByWalletDTO(RelatedWalletDTO):
    pass


class UndeterminedRelatedWalletDTO(RelatedWalletDTO):
    pass


class WalletRelatedWalletsDTO(BaseModel):
    similar_wallets: List[SimilarWalletDTO] = []
    copying_wallets: List[CopyingWalletDTO] = []
    copied_by_wallets: List[CopiedByWalletDTO] = []
    undetermined_wallets: List[UndeterminedRelatedWalletDTO] = []
