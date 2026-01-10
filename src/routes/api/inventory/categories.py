from typing import Annotated

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import JSONResponse

from .... import utils
from ....depedencies import is_authenticated, user_permissions
from ....exceptions import DatabaseException
from ....helpers import Database
from ....models.inventory import Category
from ....utils import Permissions

categories_router = APIRouter(
    prefix="/categories", dependencies=[Depends(is_authenticated)])

db = Database()


@categories_router.get("", response_class=JSONResponse)
async def list_categories(request: Request, user_perms: list[str] = Depends(user_permissions)):
    utils.check_user_permissions(
        user_perms,
        Permissions.inventory.manage_inventory,
        Permissions.inventory.view_inventory,
        Permissions.inventory.manage_categories,
        Permissions.inventory.view_categories
    )

    return db.fetchAll(r'SELECT * FROM categories')


@categories_router.post("/add", response_class=JSONResponse)
async def add_category(request: Request, category_name: str = Form(), user_perms: list[str] = Depends(user_permissions)):
    utils.check_user_permissions(
        user_perms,
        Permissions.inventory.manage_inventory,
        Permissions.inventory.manage_categories,
    )

    try:

        if category_name.strip() == "":
            raise DatabaseException("category_name is empty.")

        db.commitOne(
            r'INSERT INTO categories (category_name) VALUES (%s)', (category_name,))

        return JSONResponse({
            "success": True,
            "message": "Successfully Added Category."
        }, status_code=201)
    except Exception as e:
        return JSONResponse({
            "success": False,
            "message": f"{e}"
        },
            status_code=400
        )


@categories_router.post("/update", response_class=JSONResponse)
async def edit_category(request: Request, category: Annotated[Category, Form()], user_perms: list[str] = Depends(user_permissions)):
    utils.check_user_permissions(
        user_perms,
        Permissions.inventory.manage_inventory,
        Permissions.inventory.manage_categories,
    )
    try:

        if category.category_id < 0:
            raise DatabaseException("category_id cannot be negative")

        if category.category_name.strip() == "":
            raise DatabaseException("category_name is empty.")

        db.commitOne(
            r'UPDATE categories SET category_name = %s WHERE category_id = %s', (category.category_name, category.category_id))

        return {
            "success": True,
            "message": f"Successfully Updated Category."
        }
    except Exception as e:
        return JSONResponse({
            "success": False,
            "message": f"{e}"
        },
            status_code=400
        )


@categories_router.delete("/delete/")
async def delete_category(request: Request, category_id: int, user_perms: list[str] = Depends(user_permissions)):
    utils.check_user_permissions(
        user_perms,
        Permissions.inventory.manage_inventory,
        Permissions.inventory.manage_categories,
    )

    try:
        rowCount = db.commitOne(
            r'DELETE FROM categories WHERE category_id = %s', (category_id,)).rowcount

        if rowCount <= 0:
            raise DatabaseException("category_id doesn't exist.")

        return {
            "success": True,
            "message": f"Successfully Deleted Category."
        }
    except Exception as e:
        return JSONResponse({
            "success": False,
            "message": f"{e}"
        },
            status_code=400
        )


@categories_router.get("/{category_id}", response_class=JSONResponse)
async def fetch_category(request: Request, category_id: int, user_perms: list[str] = Depends(user_permissions)):
    utils.check_user_permissions(
        user_perms,
        Permissions.inventory.manage_inventory,
        Permissions.inventory.view_inventory,
        Permissions.inventory.manage_categories,
        Permissions.inventory.view_categories
    )

    return db.fetchOne(r'SELECT * FROM categories WHERE category_id = %s', (category_id,))
