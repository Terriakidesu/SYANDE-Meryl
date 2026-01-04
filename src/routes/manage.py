from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates

from .. import utils
from ..depedencies import is_authenticated, user_permissions
from ..utils import Permissions

manage_router = APIRouter(prefix="/manage",
                          dependencies=[Depends(is_authenticated)])

templates = Jinja2Templates("assets/public/templates/manage")


@manage_router.get("/")
async def dashboard(request: Request):
    return templates.TemplateResponse(request, "dashboard.html")
