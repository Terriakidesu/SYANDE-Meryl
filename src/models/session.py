
from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from ..Settings import Settings


class Session(BaseModel):
    authenticated: bool = False
    user_id: Optional[int] = None
    username: Optional[str] = ""
    email: Optional[str] = ""

    otp: Optional[str] = ""
    otp_timeestamp: float = datetime.now().timestamp()
    otp_cooldown_timestamp: float = datetime.now().timestamp()

    logged_at: float = datetime.now().timestamp()
