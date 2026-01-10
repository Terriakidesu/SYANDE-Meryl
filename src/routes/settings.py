
from fastapi import APIRouter, Request, Depends

from ..depedencies import is_authenticated

settings_router = APIRouter(
    "/settings", dependencies=[Depends(is_authenticated)])
