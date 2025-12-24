from typing import Optional
from pydantic import BaseModel

class Secrets(BaseModel):
    db_hostname:Optional[str]
    db_username:Optional[str]
    db_password:Optional[str]