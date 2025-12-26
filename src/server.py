import logging
from fastapi import FastAPI, Request
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from .routes.api import (
    auth_router,
    inventory_router,
    management_router,
    sales_router,
    users_router
)
from .Settings import Settings

logger = logging.getLogger(__name__)

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        logger.info(f"Request: {request.method} {request.url}")
        response = await call_next(request)
        logger.info(f"Response: {response.status_code}")
        return response

app = FastAPI()

# Setup logging
logging.basicConfig(
    level=getattr(logging, Settings.logging.level.upper(), logging.INFO),
    format=Settings.logging.format,
    handlers=[
        logging.StreamHandler(),
        *(logging.FileHandler(Settings.logging.file) for _ in [None] if Settings.logging.file)
    ]
)

# Add middlewares
app.add_middleware(LoggingMiddleware)
app.add_middleware(SessionMiddleware, secret_key=Settings.secrets.session_secret_key)

app.include_router(auth_router)
app.include_router(management_router)
app.include_router(inventory_router)
app.include_router(users_router)
app.include_router(sales_router)


@app.get("/")
async def home():
    return "Hello"


@app.get("/endpoints")
async def list_endpoints(request: Request):
    url_list = [
        f"{route.methods} - {route.path}" for route in request.app.routes
    ]

    return url_list
