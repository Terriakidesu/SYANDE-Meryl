import logging
from pathlib import Path

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.sessions import SessionMiddleware

from .routes.api import api_router
from .routes.manage import manage_router
from .routes.pos import pos_router
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


@app.get("/logout")
async def logout(request: Request):

    if request.session.get("authenticated"):
        request.session["authenticated"] = False

    return RedirectResponse("/")


@app.get("/register")
async def register(request: Request):

    if request.session.get("authenticated"):
        return RedirectResponse("/")

    return templates.TemplateResponse(request, "register.html")


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse("favicon.ico")


@app.get("/profile")
async def get_profile_picture(request: Request, user_id: int):

    filename = f"user-{user_id:04d}"

    profiles_path = Path("assets", "public", "profiles")
    profile_path = profiles_path.joinpath(filename)

    if profile_path.exists():
        return FileResponse(profile_path.joinpath(f"{filename}.jpeg"))

    return FileResponse(profiles_path.joinpath("default", "default.jpeg"))


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
async def unauthorized_handler(request: Request, exception: HTTPException):

    if request.method == "GET":
        if exception.detail == "Session Expired":
            return RedirectResponse("/")

        

    return JSONResponse(
        {
            "success": False,
            "message": f"{exception}"
        },
        status_code=401
    )
