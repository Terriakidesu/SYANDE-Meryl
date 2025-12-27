import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from .routes.api import api_router
from .Settings import Settings, setup_logging

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        logger.info(f"Request: {request.method} {request.url}")
        response = await call_next(request)
        logger.info(f"Response: {response.status_code}")
        return response


app = FastAPI()

# Setup logging
setup_logging()

# Add middlewares
app.add_middleware(LoggingMiddleware)
app.add_middleware(SessionMiddleware,
                   secret_key=Settings.secrets.session_secret_key)

app.include_router(api_router)


@app.get("/")
async def home():
    return "Hello"


@app.get("/endpoints")
async def list_endpoints(request: Request):
    url_list = [
        f"{route.methods} - {route.path}" for route in request.app.routes
    ]

    return url_list


@app.exception_handler(401)
async def unauthorized_handler(request: Request, exception):

    return JSONResponse(
        {
            "success": False,
            "message": f"{exception}"
        },
        status_code=401
    )
