from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates

from ..depedencies import is_authenticated, user_permissions
from ..utils import Permissions
from ..helpers import sidebar

manage_router = APIRouter(prefix="/manage",
                          dependencies=[Depends(is_authenticated)])

templates = Jinja2Templates("assets/public/templates/manage")


@manage_router.get("/")
async def dashboard(request: Request):

    return templates.TemplateResponse(request, "dashboard.html", {
        "user_id": request.session.get("user_id"),
        "username": request.session.get("username"),
        "page_title": "Dashboard",
        "navigation_inventory": await sidebar.generate_sidebar_data(request, "Inventory"),
        "navigation_sales": await sidebar.generate_sidebar_data(request, "Sales"),
        "navigation_management": await sidebar.generate_sidebar_data(request, "Management"),
    })
