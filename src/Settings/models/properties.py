
from pydantic import BaseModel


class EnvironmentSettings(BaseModel):
    path: str


class ProfileSettings(BaseModel):
    path: str
    size: int
    default: str


class SessionSettings(BaseModel):
    timeout: int


class ProductSettings(BaseModel):
    path: str
    size: int
    default: str


class Properties(BaseModel):
    env: EnvironmentSettings
    profiles: ProfileSettings
    session: SessionSettings
    products: ProductSettings
