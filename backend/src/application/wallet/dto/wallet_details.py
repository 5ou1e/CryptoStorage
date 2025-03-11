from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class WalletDetailsDTO(BaseModel):
    is_scammer: Optional[bool]
    is_bot: Optional[bool]
    last_activity_timestamp: Optional[datetime] = None

    class Config:
        from_attributes = True
