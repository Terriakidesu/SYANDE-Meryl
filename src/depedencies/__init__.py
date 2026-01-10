from datetime import datetime

from fastapi import Request, HTTPException

from ..helpers import Database
from ..Settings import Settings
from ..models.session import Session
from ..utils import Permissions

db = Database()


async def is_authenticated(request: Request):
    if request.session.get("authenticated", False):

        session = Session(**request.session)

        logged_at = datetime.fromtimestamp(session.logged_at)
        now = datetime.now()

        elapsed_time = now - logged_at

        # ignore timeout
        if request.session.get("superadmin"):
            return True

        if elapsed_time.total_seconds() >= (Settings.session.timeout * 60):
            request.session.clear()
            raise HTTPException(status_code=401, detail="Session Expired")

        return True
    raise HTTPException(status_code=401, detail="Unauthorized Access")


async def user_permissions(request: Request) -> list[str]:

    if request.session.get("superadmin"):
        return [Permissions.management.admin_all]

    user_id = request.session.get("user_id")

    permissions = db.fetchAll(r"""
                              SELECT permission_code
                              FROM user_roles ur
                              JOIN role_permissions rp ON rp.role_id = ur.role_id
                              JOIN permissions p ON rp.permission_id = p.permission_id
                              WHERE ur.user_id = %s
                              """, (user_id,))

    permissions = [permission["permission_code"] for permission in permissions]

    return permissions
