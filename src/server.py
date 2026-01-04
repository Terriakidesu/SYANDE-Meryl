import logging
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, RedirectResponse, FileResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from .routes.api import api_router
from .routes.pos import pos_router
from .routes.manage import manage_router
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
app.include_router(pos_router)
app.include_router(manage_router)


app.mount("/static", StaticFiles(directory="assets/public/static"), name="static")
templates = Jinja2Templates(directory="assets/public/templates")


@app.get("/")
async def home(request: Request):

    if not request.session.get("authenticated"):
        return RedirectResponse("/login")

    return templates.TemplateResponse(request, "index.html")


@app.get("/login")
async def login(request: Request):

    if request.session.get("authenticated"):
        return RedirectResponse("/")

    return templates.TemplateResponse(request, "login.html")


@app.get("/register")
async def register(request: Request):

    if request.session.get("authenticated"):
        return RedirectResponse("/")

    return templates.TemplateResponse(request, "register.html")


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse("favicon.ico")


@app.get("/clearSession")
async def clear_session(request: Request):

    request.session.clear()

    return RedirectResponse("/")


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
