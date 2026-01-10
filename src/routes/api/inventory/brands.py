import math
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Form, Query, Request
from fastapi.responses import JSONResponse

from .... import utils
from ....depedencies import user_permissions, is_authenticated
from ....exceptions import DatabaseException
from ....helpers import Database
from ....models.inventory import Brand
from ....utils import Permissions

brands_router = APIRouter(
    prefix="/brands", dependencies=[Depends(is_authenticated)])

db = Database()


@brands_router.get("", response_class=JSONResponse)
async def list_brands(request: Request,
                      query: Annotated[Optional[str], Query()] = None,
                      page: Annotated[Optional[int], Query()] = 1,
                      limit: Annotated[Optional[int], Query()] = 10
                      ):

    count = db.fetchOne(r'SELECT COUNT(*) as count FROM brands')["count"]
    pages = math.ceil(count / limit)
    offset = (page - 1) * limit

    if query:

        result = db.fetchAll(
            r'SELECT * FROM brands WHERE brand_id = %s OR brand_name LIKE %s LIMIT %s OFFSET %s', (query, f"%{query}%", limit, offset))

        return JSONResponse({
            "result": result,
            "count": count,
            "pages": pages
        })

    result = db.fetchAll(
        r'SELECT * FROM brands LIMIT %s OFFSET %s', (limit, offset))

    return JSONResponse({
        "result": result,
        "count": count,
        "pages": pages
    })


@brands_router.post("/add", response_class=JSONResponse)
async def add_brand(request: Request, brand_name: str = Form(), user_perms: list[str] = Depends(user_permissions)):

    utils.check_user_permissions(
        user_perms,
        Permissions.inventory.manage_inventory,
        Permissions.inventory.manage_brands,
    )

    try:

        if brand_name.strip() == "":
            raise DatabaseException("brand_name is empty.")

        if _ := db.fetchOne(r'SELECT * FROM brands WHERE brand_name = %s', (brand_name.strip(),)):
            raise Exception("Brand is already exists.")

        db.commitOne(
            r'INSERT INTO brands (brand_name) VALUES (%s)', (brand_name,))

        return JSONResponse({
            "success": True,
            "message": "Successfully Added Brand."
        }, status_code=201)
    except Exception as e:
        return JSONResponse({
            "success": False,
            "message": f"{e}"
        },
            status_code=400
        )


@brands_router.post("/update", response_class=JSONResponse)
async def edit_brand(request: Request, brand: Annotated[Brand, Form()], user_perms: list[str] = Depends(user_permissions)):

    utils.check_user_permissions(
        user_perms,
        Permissions.inventory.manage_inventory,
        Permissions.inventory.manage_brands,
    )

    try:

        if brand.brand_id < 0:
            raise DatabaseException("brand_id cannot be negative")

        if brand.brand_name.strip() == "":
            raise DatabaseException("brand_name is empty.")

        if _ := db.fetchOne(r'SELECT * FROM brands WHERE brand_name = %s', (brand.brand_name.strip(),)):
            raise Exception("Brand is already exists.")

        db.commitOne(
            r'UPDATE brands SET brand_name = %s WHERE brand_id = %s', (brand.brand_name, brand.brand_id))

        return {
            "success": True,
            "message": f"Successfully Updated Brand."
        }
    except Exception as e:
        return JSONResponse({
            "success": False,
            "message": f"{e}"
        },
            status_code=400
        )


@brands_router.delete("/delete/{brand_id}")
async def delete_brand(request: Request, brand_id: int, user_perms: list[str] = Depends(user_permissions)):

    utils.check_user_permissions(
        user_perms,
        Permissions.inventory.manage_inventory,
        Permissions.inventory.manage_brands,
    )

    try:
        rowCount = db.commitOne(
            r'DELETE FROM brands WHERE brand_id = %s', (brand_id,)).rowcount

        if rowCount <= 0:
            raise DatabaseException("brand_id doesn't exist.")

        return {
            "success": True,
            "message": f"Successfully Deleted Brand."
        }
    except Exception as e:
        return JSONResponse({
            "success": False,
            "message": f"{e}"
        },
            status_code=400
        )


@brands_router.get("/{brand_id}", response_class=JSONResponse)
async def fetch_brand(request: Request, brand_id: int):

    return db.fetchOne(r'SELECT * FROM brands WHERE brand_id = %s', (brand_id,))
