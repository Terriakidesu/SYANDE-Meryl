
from typing import List, Optional
from pydantic import BaseModel


class EnvironmentSettings(BaseModel):
    name: str
    path: str
    debug: bool = False


class DatabaseSettings(BaseModel):
    pool_size: int = 10
    max_overflow: int = 20
    pool_timeout: int = 30
    pool_recycle: int = 3600


class ApiSettings(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 4
    reload: bool = True
    cors_origins: List[str] = []


class LoggingSettings(BaseModel):
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file: Optional[str] = None
    max_file_size: int = 10485760
    backup_count: int = 5


class SecuritySettings(BaseModel):
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7


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


class CacheSettings(BaseModel):
    enabled: bool = True
    ttl: int = 300
    max_size: int = 1000


class RateLimitingSettings(BaseModel):
    enabled: bool = True
    requests_per_minute: int = 60
    burst_limit: int = 10


class Properties(BaseModel):
    env: EnvironmentSettings
    database: DatabaseSettings = DatabaseSettings()
    api: ApiSettings = ApiSettings()
    logging: LoggingSettings = LoggingSettings()
    security: SecuritySettings
    profiles: ProfileSettings
    products: ProductSettings
    session: SessionSettings
    cache: CacheSettings = CacheSettings()
    rate_limiting: RateLimitingSettings = RateLimitingSettings()
