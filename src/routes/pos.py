from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates

from .. import utils
from ..depedencies import is_authenticated, user_permissions
from ..utils import Permissions

pos_router = APIRouter(prefix="/pos",
                       dependencies=[Depends(is_authenticated)])

templates = Jinja2Templates("assets/public/templates/pos")


@pos_router.get("/")
async def POS(request: Request, user_perms: Annotated[list[str], Depends(user_permissions)]):
    utils.check_user_permissions(user_perms, Permissions.pos.use_pos)

    return templates.TemplateResponse("pos.html", request=request)
