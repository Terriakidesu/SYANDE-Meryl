from typing import Optional
from pydantic import BaseModel

class Secrets(BaseModel):
    db_hostname:Optional[str]
    db_username:Optional[str]
    db_password:Optional[str]
    db_database:Optional[str]

    session_secret_key: str

    resend_api_key: str

    gmail_client_id: str
    gmail_client_secret: str
    gmail_refresh_token: str
