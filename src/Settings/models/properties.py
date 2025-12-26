
from typing import List
from pydantic import BaseModel


class EnvironmentSettings(BaseModel):
    name: str
    path: str
    debug: bool = False





class ProfileSettings(BaseModel):
    path: str
    size: int
    default: str
    quality: int = 85
    supported_formats: List[str] = ["JPEG", "PNG"]


class ProductSettings(BaseModel):
    path: str
    size: int
    default: str
    quality: int = 85
    supported_formats: List[str] = ["JPEG", "PNG"]
    max_file_size: int = 5242880


class SessionSettings(BaseModel):
    timeout: int
    cookie_name: str = "session_id"
    secure: bool = False
    httponly: bool = True



class Properties(BaseModel):
    env: EnvironmentSettings
    profiles: ProfileSettings
    products: ProductSettings
    session: SessionSettings
