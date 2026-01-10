import math
from typing import Optional, Annotated

from fastapi import APIRouter, Request, Form, Depends, Query
from fastapi.responses import JSONResponse

from ...depedencies import is_authenticated
from ...helpers import Database
from ...exceptions import DatabaseException

management_router = APIRouter(prefix="", dependencies=[
                              Depends(is_authenticated)])

db = Database()


@management_router.get("/roles", response_class=JSONResponse)
async def list_roles(request: Request,
                     query: Annotated[Optional[str], Query()] = None,
                     page: Annotated[Optional[int], Query()] = 1,
                     limit: Annotated[Optional[int], Query()] = 10):

    count = db.fetchOne(r'SELECT COUNT(*) as count FROM roles')["count"]
    pages = math.ceil(count / limit)
    offset = (page - 1) * limit

    # Fetch results based on query
    if query:
        results = db.fetchAll(
            r"""
            SELECT * FROM roles
            WHERE role_id = %s OR role_name LIKE %s
            LIMIT %s OFFSET %s
            """,
            (query, f"%{query}%", limit, offset)
        )
    else:
        results = db.fetchAll(
            r"""
            SELECT * FROM roles
            LIMIT %s OFFSET %s
            """,
            (limit, offset)
        )

    return JSONResponse({
        "result": results,
        "count": count,
        "pages": pages
    })


@management_router.post("/roles/add", response_class=JSONResponse)
async def add_role(request: Request, role_name: str = Form(), permission_ids: Optional[str] = Form(None)):
    try:
        if role_name.strip() == "":
            raise DatabaseException("role_name is empty.")

        # Check if role already exists
        if db.fetchOne(r'SELECT * FROM roles WHERE role_name = %s', (role_name,)):
            raise DatabaseException("Role name already exists.")

        cursor = db.commitOne(
            r'INSERT INTO roles (role_name) VALUES (%s)', (role_name,))

        role_id = cursor.lastrowid

        if permission_ids:
            # Parse and validate permission_ids
            permission_list = []
            for pid in permission_ids.split(","):
                pid = pid.strip()
                if pid:
                    try:
                        perm_id = int(pid)
                        permission_list.append(perm_id)
                    except ValueError:
                        raise DatabaseException(
                            f"Invalid permission ID: {pid}")

            # Check if permissions exist
            if permission_list:
                placeholders = ','.join(['%s'] * len(permission_list))
                existing_perms = db.fetchAll(
                    f'SELECT permission_id FROM permissions WHERE permission_id IN ({placeholders})',
                    tuple(permission_list)
                )
                existing_perm_ids = {p['permission_id']
                                     for p in existing_perms}

                if len(existing_perm_ids) != len(permission_list):
                    missing = set(permission_list) - existing_perm_ids
                    raise DatabaseException(
                        f"Permissions do not exist: {list(missing)}")

                # Insert role_permissions efficiently
                permissions = tuple((role_id, perm_id)
                                    for perm_id in permission_list)
                db.commitMany(
                    r'INSERT INTO role_permissions (role_id, permission_id) VALUES (%s, %s)', permissions)

        return JSONResponse({
            "success": True,
            "message": "Successfully Added Role.",
            "role_id": role_id
        }, status_code=201)
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

        db.commitOne(
            r'UPDATE roles SET role_name = %s WHERE role_id = %s', (role_name, role_id))

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


@management_router.delete("/roles/delete", response_class=JSONResponse)
async def delete_role(request: Request, role_id: int = Form()):
    try:
        rowCount = db.commitOne(
            r'DELETE FROM roles WHERE role_id = %s', (role_id,)).rowcount

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


@management_router.get("/roles/{role_id}", response_class=JSONResponse)
async def fetch_role(request: Request, role_id: int):
    return db.fetchOne(r"SELECT * FROM roles WHERE role_id = %s", (role_id,))


@management_router.get("/roles/{role_id}/permissions/")
async def list_role_permissions(request: Request, role_id: int):
    return db.fetchAll(r"""
                    SELECT p.*
                    FROM role_permissions rp
                    JOIN permissions p ON rp.permission_id = p.permission_id
                    """)

# @management_router.post("/roles/{role_id}/permissions/add")
# async def add_role_permission(request: Request, role_id:int, permission_id: int):

#     if role_id < 0 or permission_id < 0:
#         return {
#             "success" : False,
#             "message": "role_id or permission_id is invalid."
#         }

#     if role := db.fetchOne('SELECT * FROM roles WHERE role_id = %s', (role_id,)):

#         db.commitOne('')


@management_router.get("/permissions", response_class=JSONResponse)
async def list_permissions(request: Request):
    return db.fetchAll(r"SELECT * from permissions")


@management_router.get("/permissions/{permission_id}", response_class=JSONResponse)
async def fetch_permission(request: Request, permission_id: int):
    return db.fetchOne(r"SELECT * FROM permissions WHERE permission_id = %s", (permission_id,))


@management_router.get("/userRoles", response_class=JSONResponse)
async def list_user_roles(request: Request):
    return db.fetchAll(r'SELECT * from user_roles')


@management_router.get("/rolePerms", response_class=JSONResponse)
async def list_all_role_permissions(request: Request):
    return db.fetchAll(r'SELECT * from role_permissions')
