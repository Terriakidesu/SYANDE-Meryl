
from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from ..Settings import Settings


class Session(BaseModel):
    authenticated: bool = False
    user_id: Optional[int] = None
    username: Optional[str] = ""

    logged_at: float = datetime.now().timestamp()
