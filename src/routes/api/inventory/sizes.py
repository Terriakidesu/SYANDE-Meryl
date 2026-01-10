import math
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Form, Query, Request
from fastapi.responses import JSONResponse

from .... import utils
from ....depedencies import is_authenticated, user_permissions
from ....exceptions import DatabaseException
from ....helpers import Database
from ....utils import Permissions

sizes_router = APIRouter(prefix="/sizes", dependencies=[Depends(is_authenticated)])

db = Database()


@sizes_router.get("", response_class=JSONResponse)
async def list_sizes(request: Request,
                     query: Annotated[Optional[str], Query()] = None,
                     page: Annotated[Optional[int], Query()] = 1,
                     limit: Annotated[Optional[int], Query()] = 10
                     ):

    count = db.fetchOne(r'SELECT COUNT(*) as count FROM sizes')["count"]
    pages = math.ceil(count / limit)
    offset = (page - 1) * limit

    if query:
        result = db.fetchAll(
            r'SELECT * FROM sizes WHERE size_id = %s OR us_size LIKE %s OR uk_size LIKE %s OR eu_size LIKE %s LIMIT %s OFFSET %s', (query, f"%{query}%", f"%{query}%", f"%{query}%", limit, offset))

        return JSONResponse({
            "result": result,
            "count": count,
            "pages": pages
        })

    result = db.fetchAll(
        r'SELECT * FROM sizes LIMIT %s OFFSET %s', (limit, offset))

    return JSONResponse({
        "result": result,
        "count": count,
        "pages": pages
    })


@sizes_router.post("/add", response_class=JSONResponse)
async def add_size(request: Request,
                   us_size: float = Form(),
                   uk_size: float = Form(),
                   eu_size: float = Form(),
                   user_perms: list[str] = Depends(user_permissions)):
    utils.check_user_permissions(
        user_perms,
        Permissions.inventory.manage_inventory,
        Permissions.inventory.manage_sizes,
    )

    try:

        if us_size <= 0:
            raise DatabaseException("us_size cannot be zero or negative.")

        if uk_size <= 0:
            raise DatabaseException("uk_size cannot be zero or negative.")

        if eu_size <= 0:
            raise DatabaseException("eu_size cannot be zero or negative.")

        db.commitOne(
            r'INSERT INTO sizes (us_size, uk_size, eu_size) VALUES (%s, %s, %s)', (us_size, uk_size, eu_size))

        return JSONResponse({
            "success": True,
            "message": "Successfully Added Size."
        }, status_code=201)
    except Exception as e:
        return JSONResponse({
            "success": False,
            "message": f"{e}"
        },
            status_code=400
        )


@sizes_router.post("/update", response_class=JSONResponse)
async def edit_size(request: Request,
                    size_id: int = Form(),
                    us_size: float = Form(),
                    uk_size: float = Form(),
                    eu_size: float = Form(),
                    user_perms: list[str] = Depends(user_permissions)):
    utils.check_user_permissions(
        user_perms,
        Permissions.inventory.manage_inventory,
        Permissions.inventory.manage_sizes,
    )

    try:

        if size_id <= 0:
            raise DatabaseException("size_id cannot be zero or negative.")

        if us_size <= 0:
            raise DatabaseException("us_size cannot be zero or negative.")

        if uk_size <= 0:
            raise DatabaseException("uk_size cannot be zero or negative.")

        if eu_size <= 0:
            raise DatabaseException("eu_size cannot be zero or negative.")

        db.commitOne(
            r'UPDATE sizes SET us_size = %s, uk_size = %s, eu_size = %s WHERE size_id = %s', (us_size, uk_size, eu_size, size_id))

        return {
            "success": True,
            "message": f"Successfully Updated Size."
        }
    except Exception as e:
        return JSONResponse({
            "success": False,
            "message": f"{e}"
        },
            status_code=400
        )


@sizes_router.delete("/delete/{size_id}")
async def delete_size(request: Request, size_id: int, user_perms: list[str] = Depends(user_permissions)):
    utils.check_user_permissions(
        user_perms,
        Permissions.inventory.manage_inventory,
        Permissions.inventory.manage_sizes,
    )

    try:
        rowCount = db.commitOne(
            r'DELETE FROM sizes WHERE size_id = %s', (size_id,)).rowcount

        if rowCount <= 0:
            raise DatabaseException("size_id doesn't exist.")

        return {
            "success": True,
            "message": f"Successfully Deleted Size."
        }
    except Exception as e:
        return JSONResponse({
            "success": False,
            "message": f"{e}"
        },
            status_code=400
        )


@sizes_router.get("/{size_id}", response_class=JSONResponse)
async def fetch_size(request: Request, size_id: int, user_perms: list[str] = Depends(user_permissions)):
    utils.check_user_permissions(
        user_perms,
        Permissions.inventory.manage_inventory,
        Permissions.inventory.view_inventory,
        Permissions.inventory.manage_sizes,
        Permissions.inventory.view_sizes
    )

    return db.fetchOne(r'SELECT * FROM sizes WHERE size_id = %s', (size_id,))
