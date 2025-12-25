
from pydantic import BaseModel


class Env(BaseModel):
    path: str


class Profiles(BaseModel):
    path: str
    size: int
    default: str


class Session(BaseModel):
    timeout: int


class Properties(BaseModel):
    env: Env
    profiles: Profiles
    session: Session
