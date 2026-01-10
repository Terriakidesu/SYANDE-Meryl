
from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates

from ..depedencies import is_authenticated

settings_router = APIRouter(
    prefix="/settings", dependencies=[Depends(is_authenticated)])


templates = Jinja2Templates("assets/public/templates/")


@settings_router.get("/")
async def settings_home(request: Request):
    return templates.TemplateResponse(request, "settings/index.html", {
        "user_id": request.session["user_id"],
        "username": request.session["username"],
        "page_title": "Settings",
        "navigation_management": [
            {
                "caption": "Profile Settings",
                "href": "/settings/profile",
                "icon": "fa-user-gear"
            }
        ]
    })


@settings_router.get("/profile")
async def settings_home(request: Request):
    return templates.TemplateResponse(request, "settings/profile.html", {
        "user_id": request.session["user_id"],
        "username": request.session["username"],
        "page_title": "Profile Settings"
    })


@settings_router.get("/change-password")
async def change_password(request: Request):
    return templates.TemplateResponse(request, "settings/change-password.html", {
        "user_id": request.session["user_id"],
        "username": request.session["username"],
        "page_title": "Change Password"
    })
