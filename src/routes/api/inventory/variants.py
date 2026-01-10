from typing import Annotated

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import JSONResponse

from .... import utils
from ....depedencies import is_authenticated, user_permissions
from ....exceptions import DatabaseException
from ....helpers import Database
from ....models.inventory import Variant
from ....utils import Permissions

variants_router = APIRouter(
    prefix="/variants", dependencies=[Depends(is_authenticated)])

db = Database()


@variants_router.get("", response_class=JSONResponse)
async def list_variants(request: Request, user_perms: list[str] = Depends(user_permissions)):
    utils.check_user_permissions(
        user_perms,
        Permissions.inventory.manage_inventory,
        Permissions.inventory.view_inventory,
        Permissions.inventory.manage_variants,
        Permissions.inventory.view_variants
    )

    return db.fetchAll(r'SELECT * FROM variants')


@variants_router.post("/add", response_class=JSONResponse)
async def add_variant(request: Request,
                      shoe_id: int = Form(),
                      size_id: int = Form(),
                      variant_stock: int = Form(),
                      user_perms: list[str] = Depends(user_permissions)
                      ):

    utils.check_user_permissions(
        user_perms,
        Permissions.inventory.manage_inventory,
        Permissions.inventory.manage_variants,
    )

    try:

        if shoe_id is None or shoe_id < 0:
            raise DatabaseException("shoe_id is invalid.")

        if size_id is None or size_id < 0:
            raise DatabaseException("size_id is invalid.")

        if variant_stock is None or variant_stock < 0:
            raise DatabaseException("variant_stock is invalid.")

        db.commitOne(
            r'INSERT INTO variants (shoe_id, size_id, variant_stock) VALUES (%s, %s, %s)', (shoe_id, size_id, variant_stock))

        return JSONResponse({
            "success": True,
            "message": "Successfully Added Variant."
        }, status_code=201)
    except Exception as e:
        return JSONResponse({
            "success": False,
            "message": f"{e}"
        },
            status_code=400
        )


@variants_router.post("/update", response_class=JSONResponse)
async def edit_variant(request: Request, variant: Annotated[Variant, Form()], user_perms: list[str] = Depends(user_permissions)):
    utils.check_user_permissions(
        user_perms,
        Permissions.inventory.manage_inventory,
        Permissions.inventory.manage_variants,
    )
    try:

        if variant.variant_id is None or variant.variant_id < 0:
            raise DatabaseException("variant_id is invalid.")

        if variant.shoe_id is None or variant.shoe_id < 0:
            raise DatabaseException("shoe_id is invalid.")

        if variant.size_id is None or variant.size_id < 0:
            raise DatabaseException("size_id is invalid.")

        if variant.variant_stock is None or variant.variant_stock < 0:
            raise DatabaseException("variant_stock is invalid.")

        db.commitOne(
            r'UPDATE variants SET shoe_id = %s, size_id = %s, variant_stock = %s WHERE variant_id = %s',
            (variant.shoe_id, variant.size_id,
             variant.variant_stock, variant.variant_id)
        )

        return {
            "success": True,
            "message": f"Successfully Updated Variant."
        }
    except Exception as e:
        return JSONResponse({
            "success": False,
            "message": f"{e}"
        },
            status_code=400
        )


@variants_router.delete("/delete/")
async def delete_variant(request: Request, variant_id: int, user_perms: list[str] = Depends(user_permissions)):
    utils.check_user_permissions(
        user_perms,
        Permissions.inventory.manage_inventory,
        Permissions.inventory.manage_variants,
    )

    try:
        rowCount = db.commitOne(
            r'DELETE FROM variants WHERE variant_id = %s', (variant_id,)).rowcount

        if rowCount <= 0:
            raise DatabaseException("variant_id doesn't exist.")

        return {
            "success": True,
            "message": f"Successfully Deleted Variant."
        }
    except Exception as e:
        return JSONResponse({
            "success": False,
            "message": f"{e}"
        },
            status_code=400
        )


@variants_router.get("/{variant_id}", response_class=JSONResponse)
async def fetch_variant(request: Request, variant_id: int, user_perms: list[str] = Depends(user_permissions)):
    utils.check_user_permissions(
        user_perms,
        Permissions.inventory.manage_inventory,
        Permissions.inventory.view_inventory,
        Permissions.inventory.manage_variants,
        Permissions.inventory.view_variants
    )

    return db.fetchOne(r'SELECT * FROM variants WHERE variant_id = %s', (variant_id,))
