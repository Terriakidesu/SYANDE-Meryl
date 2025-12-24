from typing import Optional

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from ...includes import Database

users_router = APIRouter(prefix="/api/users")

db = Database()


@users_router.get("/", response_class=JSONResponse)
async def list_users(request: Request):
    return db.fetchAll(r'SELECT * FROM users')


@users_router.get("/{user_id}", response_class=JSONResponse)
async def fetch_user(request: Request, user_id: Optional[int] = None):

    if user_id is None:
        return []

    return db.fetchAll(r'SELECT * FROM users WHERE user_id = %s', (user_id,))


@users_router.get("/{user_id}/phone", response_class=JSONResponse)
async def list_user_phone(request: Request, user_id: int):

    return db.fetchAll(r'SELECT * FROM phones WHERE user_id = %s', (user_id, ))


@users_router.get("/{user_id}/emails", response_class=JSONResponse)
async def list_user_emails(request: Request, user_id: int):

    return db.fetchAll(r'SELECT * FROM emails WHERE user_id = %s', (user_id, ))


@users_router.get("/{user_id}/roles", response_class=JSONResponse)
async def list_user_roles(request: Request, user_id: int):

    return db.fetchAll(r'SELECT * FROM user_roles WHERE user_id = %s', (user_id, ))


@users_router.get("/{user_id}/roles/{role_id}", response_class=JSONResponse)
async def fetch_user_role(request: Request, user_id: int, role_id):

    return db.fetchOne(
        r'SELECT * FROM user_roles WHERE user_id = %s AND role_id = %s', (user_id, role_id))


@users_router.get("/{user_id}/roles/{role_id}/permissions", response_class=JSONResponse)
async def list_user_role_permissions(request: Request, user_id: int, role_id: int):

    role = db.fetchOne(
        r'SELECT * FROM user_roles WHERE user_id = %s AND role_id = %s', (user_id, role_id))

    if role is None:
        return []

    return db.fetchAll(r'SELECT * FROM role_permissions WHERE role_id', (role_id,))


@users_router.get("/{user_id}/roles/{role_id}/permissions/{permission_id}", response_class=JSONResponse)
async def fetch_user_role_permission(request: Request, user_id: int, role_id: int, permission_id: int):

    role = db.fetchOne(
        r'SELECT * FROM user_roles WHERE user_id = %s AND role_id = %s', (user_id, role_id))

    if role is None:
        return []

    return db.fetchAll(r'SELECT * FROM role_permissions WHERE role_id = %s AND permission_id = %s', (role_id, permission_id))
