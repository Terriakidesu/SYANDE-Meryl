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
from .routes.settings import settings_router
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
app.include_router(settings_router)


app.mount("/static", StaticFiles(directory="assets/public/static"), name="static")
templates = Jinja2Templates(directory="assets/public/templates")


@app.get("/")
async def home(request: Request):

    if not request.session.get("authenticated"):
        return RedirectResponse("/login")

    return templates.TemplateResponse(request, "index.html", {
        "user_id" : request.session["user_id"],
        "username" : request.session["username"]
    })


@app.get("/login")
async def login(request: Request):

    if request.session.get("authenticated"):
        return RedirectResponse("/")

    return templates.TemplateResponse(request, "login.html")


@app.get("/logout")
async def logout(request: Request):

    if request.session.get("authenticated"):
        request.session.clear()

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

    filename = f"user-{user_id:05d}"


    profiles_path = Path("assets", "public", "profiles")
    profile_path = profiles_path.joinpath(filename)

    if profile_path.exists():
        return FileResponse(profile_path.joinpath(f"{filename}.jpeg"))

    return FileResponse(profiles_path.joinpath("default", "default.jpeg"))

@app.get("/shoe")
async def get_shoe_image(request: Request, shoe_id: int):
    filename = f"shoe-{shoe_id:05d}"

    shoe_dir = Path(Settings.shoes.path, filename)
    image_path = shoe_dir / f"{filename}.jpeg"

    if image_path.exists():
        return FileResponse(image_path)

    return FileResponse(Settings.shoes.default)

@app.get("/clearSession")
async def clear_session(request: Request):

    request.session.clear()

    return RedirectResponse("/")


@app.exception_handler(401)
async def unauthorized_handler(request: Request, exception: HTTPException):

    if request.method == "GET":
        if exception.detail == "Session Expired":
            return RedirectResponse("/")

        print(exception)

        return templates.TemplateResponse(request, "exceptions/401-unathorized.html")

    return JSONResponse(
        {
            "success": False,
            "message": f"{exception}"
        },
        status_code=401
    )


@app.exception_handler(404)
async def not_found_handler(request: Request, exception: HTTPException):

    if request.method == "GET":

        return templates.TemplateResponse(request, "exceptions/404-not-found.html")

    return JSONResponse(
        {
            "success": False,
            "message": f"{exception}"
        },
        status_code=404
    )
