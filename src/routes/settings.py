
from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates

from ..depedencies import is_authenticated

settings_router = APIRouter(
    prefix="/settings", dependencies=[Depends(is_authenticated)])


templates = Jinja2Templates("assets/public/templates/")


@settings_router.get("/")
async def settings_home(request: Request):
    return templates.TemplateResponse(request, "settings/index.html")


@settings_router.get("/profile")
async def settings_home(request: Request):
    return templates.TemplateResponse(request, "settings/profile.html")
