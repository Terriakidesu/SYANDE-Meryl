
from typing import List, Optional
from pydantic import BaseModel


class EnvironmentSettings(BaseModel):
    name: str
    path: str
    debug: bool = False


class LoggingSettings(BaseModel):
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    path: str = "logs"
    max_file_size: int = 10485760
    backup_count: int = 5


class ProfileSettings(BaseModel):
    path: str
    size: int
    default: str
    quality: int = 85
    supported_formats: List[str] = ["JPEG", "PNG"]


class Productsettings(BaseModel):
    path: str
    size: int
    default: str
    quality: int = 85
    supported_formats: List[str] = ["JPEG", "PNG"]
    max_file_size: int = 5242880


class SessionSettings(BaseModel):
    timeout: int
    secure: bool = False
    httponly: bool = True


class Properties(BaseModel):
    env: EnvironmentSettings
    logging: LoggingSettings = LoggingSettings()
    profiles: ProfileSettings
    products: Productsettings
    session: SessionSettings
