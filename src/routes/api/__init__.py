from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from .auth import auth_router
from .inventory import inventory_router
from .management import management_router
from .sales import sales_router
from .users import users_router


api_router = APIRouter(prefix="/api")

api_router.include_router(auth_router)
api_router.include_router(inventory_router)
api_router.include_router(management_router)
api_router.include_router(sales_router)
api_router.include_router(users_router)
