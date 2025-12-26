from typing import Optional

from fastapi import APIRouter, Request, Form
from fastapi.responses import JSONResponse

from ...includes import Database
from ...exceptions import DatabaseException

management_router = APIRouter(prefix="/api")

db = Database()


@management_router.get("/roles", response_class=JSONResponse)
async def list_roles(request: Request):
    return db.fetchAll(r"SELECT * from roles")


@management_router.get("/roles/{role_id}", response_class=JSONResponse)
async def fetch_role(request: Request, role_id: int):
    return db.fetchOne(r"SELECT * FROM roles WHERE role_id = %s", (role_id,))


@management_router.post("/roles/add", response_class=JSONResponse)
async def add_role(request: Request, role_name: str = Form()):
    try:
        if role_name.strip() == "":
            raise DatabaseException("role_name is empty.")

        db.commitOne(r'INSERT INTO roles (role_name) VALUES (%s)', (role_name,))

        return {
            "success": True,
            "message": "Successfully Added Role."
        }
    except Exception as e:
        return JSONResponse({
            "success": False,
            "message": f"{e}"
        },
            status_code=400
        )


@management_router.post("/roles/update", response_class=JSONResponse)
async def edit_role(request: Request, role_id: int = Form(), role_name: str = Form()):
    try:
        if role_id < 0:
            raise DatabaseException("role_id cannot be negative")

        if role_name.strip() == "":
            raise DatabaseException("role_name is empty.")

        db.commitOne(r'UPDATE roles SET role_name = %s WHERE role_id = %s', (role_name, role_id))

        return {
            "success": True,
            "message": "Successfully Updated Role."
        }
    except Exception as e:
        return JSONResponse({
            "success": False,
            "message": f"{e}"
        },
            status_code=400
        )


@management_router.delete("/roles/delete/{role_id}", response_class=JSONResponse)
async def delete_role(request: Request, role_id: int):
    try:
        rowCount = db.commitOne(r'DELETE FROM roles WHERE role_id = %s', (role_id,)).rowcount

        if rowCount <= 0:
            raise DatabaseException("role_id doesn't exist.")

        return {
            "success": True,
            "message": "Successfully Deleted Role."
        }
    except Exception as e:
        return JSONResponse({
            "success": False,
            "message": f"{e}"
        },
            status_code=400
        )


@management_router.get("/permissions", response_class=JSONResponse)
async def list_permissions(request: Request):
    return db.fetchAll(r"SELECT * from permissions")


@management_router.get("/permissions/{permission_id}", response_class=JSONResponse)
async def fetch_permission(request: Request, permission_id: int):
    return db.fetchOne(r"SELECT * FROM permissions WHERE permission_id = %s", (permission_id,))


@management_router.post("/permissions/add", response_class=JSONResponse)
async def add_permission(request: Request, permission_name: str = Form()):
    try:
        if permission_name.strip() == "":
            raise DatabaseException("permission_name is empty.")

        db.commitOne(r'INSERT INTO permissions (permission_name) VALUES (%s)', (permission_name,))

        return {
            "success": True,
            "message": "Successfully Added Permission."
        }
    except Exception as e:
        return JSONResponse({
            "success": False,
            "message": f"{e}"
        },
            status_code=400
        )


@management_router.post("/permissions/update", response_class=JSONResponse)
async def edit_permission(request: Request, permission_id: int = Form(), permission_name: str = Form()):
    try:
        if permission_id < 0:
            raise DatabaseException("permission_id cannot be negative")

        if permission_name.strip() == "":
            raise DatabaseException("permission_name is empty.")

        db.commitOne(r'UPDATE permissions SET permission_name = %s WHERE permission_id = %s', (permission_name, permission_id))

        return {
            "success": True,
            "message": "Successfully Updated Permission."
        }
    except Exception as e:
        return JSONResponse({
            "success": False,
            "message": f"{e}"
        },
            status_code=400
        )


@management_router.delete("/permissions/delete/{permission_id}", response_class=JSONResponse)
async def delete_permission(request: Request, permission_id: int):
    try:
        rowCount = db.commitOne(r'DELETE FROM permissions WHERE permission_id = %s', (permission_id,)).rowcount

        if rowCount <= 0:
            raise DatabaseException("permission_id doesn't exist.")

        return {
            "success": True,
            "message": "Successfully Deleted Permission."
        }
    except Exception as e:
        return JSONResponse({
            "success": False,
            "message": f"{e}"
        },
            status_code=400
        )


@management_router.get("/userRoles", response_class=JSONResponse)
async def list_user_roles(request: Request):
    return db.fetchAll(r'SELECT * from user_roles')


@management_router.get("/rolePerms", response_class=JSONResponse)
async def list_all_role_permissions(request: Request):
    return db.fetchAll(r'SELECT * from role_permissions')
