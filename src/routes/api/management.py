from typing import Optional

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from ...includes import Database

management_router = APIRouter(prefix="/api/admin")

db = Database()


@management_router.get("/roles", response_class=JSONResponse)
async def list_roles(request: Request):
    return db.fetchAll(r"SELECT * from roles")


@management_router.get("/roles/{role_id}", response_class=JSONResponse)
async def fetch_role(request: Request, role_id: Optional[int] = None):
    if role_id is None:
        return []

    return db.fetchAll(r"SELECT * FROM roles WHERE role_id = %s", (role_id,))


@management_router.get("/permissions", response_class=JSONResponse)
async def list_permissions(request: Request):
    return db.fetchAll(r"SELECT * from permissions")


@management_router.get("/permissions/{permission_id}", response_class=JSONResponse)
async def fetch_permission(request: Request, permission_id: Optional[int] = None):

    if permission_id is None:
        return []

    return db.fetchAll(r"SELECT * FROM permissions WHERE permission_id = %s", (permission_id,))


@management_router.get("/userRoles", response_class=JSONResponse)
async def list_user_roles(request: Request):
    return db.fetchAll(r'SELECT * from user_roles')


@management_router.get("/rolePerms", response_class=JSONResponse)
async def list_role_permissions(request: Request):
    return db.fetchAll(r'SELECT * from role_permissions')
