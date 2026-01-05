from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates

from ..depedencies import is_authenticated, user_permissions
from ..utils import Permissions, PermissionCategory

manage_router = APIRouter(prefix="/manage",
                          dependencies=[Depends(is_authenticated)])

templates = Jinja2Templates("assets/public/templates/manage")


def check_user_permissions(user_permissions: list[str], *permissions: str):

    if Permissions.management.admin_all in user_permissions:
        return True

    for permission in permissions:
        if permission in user_permissions:
            return True

    return False


def generate_sidebar_data(request: Request):

    sidebar = []
    user_perms = user_permissions(request)

    if check_user_permissions(user_perms,
                              Permissions.management.admin_all,
                              Permissions.inventory.manage_inventory,
                              Permissions.inventory.view_inventory,
                              Permissions.inventory.view_shoes,
                              Permissions.inventory.manage_shoes
                              ):
        sidebar.append({
            "href": "inventory/shoes",
            "category": PermissionCategory.Inventory,
            "caption": "Shoes"
        })

    return sidebar


@manage_router.get("/")
async def dashboard(request: Request):
    return templates.TemplateResponse(request, "dashboard.html", {
        "user_id": request.session.get("user_id"),
        "username": request.session.get("username"),
        "page_title": "Dashboard",
        "sidebar": generate_sidebar_data(request)
    })
