from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates

from ..depedencies import is_authenticated, user_permissions
from ..utils import Permissions
from ..helpers import sidebar

manage_router = APIRouter(prefix="/manage",
                          dependencies=[Depends(is_authenticated)])

templates = Jinja2Templates("assets/public/templates")


@manage_router.get("/")
async def dashboard(request: Request):

    return templates.TemplateResponse(request, "manage/dashboard.html", {
        "user_id": request.session.get("user_id"),
        "username": request.session.get("username"),
        "page_title": "Dashboard",
        "navigation_inventory": await sidebar.generate_sidebar_data(request, "Inventory"),
        "navigation_sales": await sidebar.generate_sidebar_data(request, "Sales"),
        "navigation_management": await sidebar.generate_sidebar_data(request, "Management"),
    })


@manage_router.get("/inventory/shoes")
async def manage_shoes(request: Request):

    return templates.TemplateResponse(request, "manage/shoes.html", {
        "user_id": request.session.get("user_id"),
        "username": request.session.get("username"),
        "page_title": "Shoes",
        "navigation_inventory": await sidebar.generate_sidebar_data(request, "Inventory"),
        "navigation_sales": await sidebar.generate_sidebar_data(request, "Sales"),
        "navigation_management": await sidebar.generate_sidebar_data(request, "Management"),
    })


@manage_router.get("/inventory/variants")
async def manage_variants(request: Request):

    return templates.TemplateResponse(request, "manage/variants.html", {
        "user_id": request.session.get("user_id"),
        "username": request.session.get("username"),
        "page_title": "Variants",
        "navigation_inventory": await sidebar.generate_sidebar_data(request, "Inventory"),
        "navigation_sales": await sidebar.generate_sidebar_data(request, "Sales"),
        "navigation_management": await sidebar.generate_sidebar_data(request, "Management"),
    })


@manage_router.get("/inventory/brands")
async def manage_brands(request: Request):

    return templates.TemplateResponse(request, "manage/brands.html", {
        "user_id": request.session.get("user_id"),
        "username": request.session.get("username"),
        "page_title": "Brands",
        "navigation_inventory": await sidebar.generate_sidebar_data(request, "Inventory"),
        "navigation_sales": await sidebar.generate_sidebar_data(request, "Sales"),
        "navigation_management": await sidebar.generate_sidebar_data(request, "Management"),
    })


@manage_router.get("/inventory/sizes")
async def manage_sizes(request: Request):

    return templates.TemplateResponse(request, "manage/sizes.html", {
        "user_id": request.session.get("user_id"),
        "username": request.session.get("username"),
        "page_title": "Sizes",
        "navigation_inventory": await sidebar.generate_sidebar_data(request, "Inventory"),
        "navigation_sales": await sidebar.generate_sidebar_data(request, "Sales"),
        "navigation_management": await sidebar.generate_sidebar_data(request, "Management"),
    })


@manage_router.get("/inventory/categories")
async def manage_categories(request: Request):

    return templates.TemplateResponse(request, "manage/categories.html", {
        "user_id": request.session.get("user_id"),
        "username": request.session.get("username"),
        "page_title": "Categories",
        "navigation_inventory": await sidebar.generate_sidebar_data(request, "Inventory"),
        "navigation_sales": await sidebar.generate_sidebar_data(request, "Sales"),
        "navigation_management": await sidebar.generate_sidebar_data(request, "Management"),
    })


@manage_router.get("/sales")
async def manage_sales(request: Request):

    return templates.TemplateResponse(request, "manage/sales.html", {
        "user_id": request.session.get("user_id"),
        "username": request.session.get("username"),
        "page_title": "Sales",
        "navigation_inventory": await sidebar.generate_sidebar_data(request, "Inventory"),
        "navigation_sales": await sidebar.generate_sidebar_data(request, "Sales"),
        "navigation_management": await sidebar.generate_sidebar_data(request, "Management"),
    })


@manage_router.get("/returns")
async def manage_returns(request: Request):

    return templates.TemplateResponse(request, "manage/returns.html", {
        "user_id": request.session.get("user_id"),
        "username": request.session.get("username"),
        "page_title": "Returns",
        "navigation_inventory": await sidebar.generate_sidebar_data(request, "Inventory"),
        "navigation_sales": await sidebar.generate_sidebar_data(request, "Sales"),
        "navigation_management": await sidebar.generate_sidebar_data(request, "Management"),
    })


@manage_router.get("/users")
async def manage_users(request: Request):

    return templates.TemplateResponse(request, "manage/users.html", {
        "user_id": request.session.get("user_id"),
        "username": request.session.get("username"),
        "page_title": "Users",
        "navigation_inventory": await sidebar.generate_sidebar_data(request, "Inventory"),
        "navigation_sales": await sidebar.generate_sidebar_data(request, "Sales"),
        "navigation_management": await sidebar.generate_sidebar_data(request, "Management"),
    })


@manage_router.get("/roles")
async def manage_roles(request: Request):

    return templates.TemplateResponse(request, "manage/roles.html", {
        "user_id": request.session.get("user_id"),
        "username": request.session.get("username"),
        "page_title": "Roles",
        "navigation_inventory": await sidebar.generate_sidebar_data(request, "Inventory"),
        "navigation_sales": await sidebar.generate_sidebar_data(request, "Sales"),
        "navigation_management": await sidebar.generate_sidebar_data(request, "Management"),
    })
