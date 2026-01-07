
import math
import os
import shutil
from io import BytesIO
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, File, Form, Request, UploadFile, Query
from fastapi.responses import JSONResponse
from PIL import Image

from ... import utils
from ...depedencies import is_authenticated, user_permissions
from ...exceptions import DatabaseException
from ...includes import Database
from ...models.inventory import Brand, Category, Shoe, Size, Variant
from ...utils import Permissions

inventory_router = APIRouter(prefix="/inventory",
                             dependencies=[Depends(is_authenticated)])

db = Database()


@inventory_router.get("/shoes", response_class=JSONResponse)
async def list_shoes(request: Request):

    return db.fetchAll(r"SELECT * FROM shoes")


@inventory_router.post("/shoes/add", response_class=JSONResponse)
async def add_shoe(request: Request,
                   file: UploadFile | None = File(None),
                   shoe_name: str = Form(),
                   brand_id: int = Form(),
                   category_id: int = Form(),
                   markup: int = Form(),
                   shoe_price: float = Form(),
                   first_sale_at: str = Form(),
                   user_perms: list[str] = Depends(user_permissions)
                   ):

    utils.check_user_permissions(
        user_perms,
        Permissions.inventory.manage_inventory,
        Permissions.inventory.manage_shoes
    )

    try:
        if shoe_name.strip() == "":
            raise DatabaseException("shoe_name is empty.")

        cursor = db.commitOne(
            r'INSERT INTO shoes (shoe_name, brand_id, category_id, markup, shoe_price, first_sale_at) VALUES (%s, %s, %s, %s, %s, %s)',
            (shoe_name, brand_id, category_id,
             markup, shoe_price, first_sale_at)
        )

        shoe_id = cursor.lastrowid

        # Handle image upload
        if file is not None:
            if not file.content_type or not file.content_type.startswith("image"):
                return JSONResponse(
                    {"success": False,
                        "message": f"Uploaded file ({file.content_type}) is not an image."},
                    status_code=415
                )

            # Create shoe directory
            from ...Settings import Settings
            shoe_dir = os.path.join(
                Settings.shoes.path, f"shoe-{shoe_id:05d}")
            os.makedirs(shoe_dir, exist_ok=True)

            # Process image
            image = Image.open(file.file)
            if image.mode in ('RGBA', 'P'):
                image = image.convert("RGB")
            image = image.resize(
                (Settings.shoes.size, Settings.shoes.size))

            # Save image
            buffer = BytesIO()
            image.save(buffer, format="JPEG",
                       quality=Settings.shoes.quality)
            buffer.seek(0)

            image_path = os.path.join(
                shoe_dir, f"shoe-{shoe_id:05d}.jpeg")
            with open(image_path, "wb") as f:
                f.write(buffer.read())
        else:
            # Copy default image
            from ...Settings import Settings
            shoe_dir = os.path.join(
                Settings.shoes.path, f"shoe-{shoe_id:05d}")
            os.makedirs(shoe_dir, exist_ok=True)
            shutil.copy(Settings.shoes.default, os.path.join(
                shoe_dir, f"shoe-{shoe_id:05d}.jpeg"))

        return JSONResponse({
            "success": True,
            "message": "Successfully Added shoe."
        }, status_code=201)
    except Exception as e:
        return JSONResponse({
            "success": False,
            "message": f"{e}"
        },
            status_code=400
        )


@inventory_router.post("/shoes/update", response_class=JSONResponse)
async def edit_shoe(request: Request, shoe: Annotated[Shoe, Form()], user_perms: list[str] = Depends(user_permissions)):

    utils.check_user_permissions(
        user_perms,
        Permissions.inventory.manage_inventory,
        Permissions.inventory.manage_shoes
    )

    try:

        if shoe.brand_id < 0:
            raise DatabaseException("brand_id cannot be negative")

        if shoe.shoe_name.strip() == "":
            raise DatabaseException("brand_name is empty.")

        db.commitOne(
            r'UPDATE shoes SET shoe_name = %s, brand_id = %s, category_id = %s, markup = %s, shoe_price = %s, first_sale_at = %s  WHERE shoe_id = %s',
            (shoe.shoe_name, shoe.brand_id, shoe.category_id, shoe.markup,
             shoe.shoe_price, shoe.first_sale_at, shoe.shoe_id)
        )

        return {
            "success": True,
            "message": "Successfully Updated shoe."
        }
    except Exception as e:
        return JSONResponse({
            "success": False,
            "message": f"{e}"
        },
            status_code=400
        )


@inventory_router.delete("/shoes/delete/")
async def delete_shoe(request: Request, shoe_id: int, user_perms: list[str] = Depends(user_permissions)):

    utils.check_user_permissions(
        user_perms,
        Permissions.inventory.manage_inventory,
        Permissions.inventory.manage_shoes
    )

    try:
        rowCount = db.commitOne(
            r'DELETE FROM shoes WHERE shoe_id = %s', (shoe_id,)).rowcount

        if rowCount <= 0:
            raise DatabaseException("shoe_id doesn't exist.")

        return {
            "success": True,
            "message": "Successfully Deleted shoe."
        }
    except Exception as e:
        return JSONResponse({
            "success": False,
            "message": f"{e}"
        },
            status_code=400
        )


@inventory_router.get("/shoes/popular", response_class=JSONResponse)
async def list_popular(request: Request, limit: int = 10, user_perms: list[str] = Depends(user_permissions)):

    utils.check_user_permissions(
        user_perms,
        Permissions.inventory.manage_inventory,
        Permissions.inventory.view_inventory,
        Permissions.inventory.view_shoes
    )

    return db.fetchAll(r"""
            SELECT
                p.shoe_id,
                p.shoe_name,
                SUM(si.quantity) AS total_quantity,
                SUM(si.price) AS total_revenue
            FROM
                sales_items si
            JOIN variants v ON
                si.variant_id = v.variant_id
            JOIN shoes p ON
                v.shoe_id = p.shoe_id
            GROUP BY
                p.shoe_id,
                p.shoe_name
            ORDER BY
                total_quantity
            DESC
            LIMIT %s;
               """, (limit,))


@inventory_router.get("/shoes/{shoe_id}", response_class=JSONResponse)
async def fetch_shoe(request: Request, shoe_id: int, user_perms: list[str] = Depends(user_permissions)):

    return db.fetchOne(r'SELECT * FROM shoes WHERE shoe_id = %s', (shoe_id,))


@inventory_router.get("/shoes/{shoe_id}/all", response_class=JSONResponse)
async def fetch_shoe(request: Request, shoe_id: int, user_perms: list[str] = Depends(user_permissions)):

    if all_shoe_details := db.fetchOne(r"""
                    SELECT * 
                    FROM shoes s
                    JOIN brands b ON b.brand_id = s.brand_id
                    WHERE s.shoe_id = %s
                       """,
                                       (shoe_id,)
                                       ):

        all_shoe_details["categories"] = db.fetchAll(
            r'SELECT * FROM categories WHERE shoe_id = %s', (shoe_id,))

        return all_shoe_details

    return None


@inventory_router.get("/brands", response_class=JSONResponse)
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


@inventory_router.post("/brands/add", response_class=JSONResponse)
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


@inventory_router.post("/brands/update", response_class=JSONResponse)
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


@inventory_router.delete("/brands/delete/{brand_id}")
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


@inventory_router.get("/brands/{brand_id}", response_class=JSONResponse)
async def fetch_brand(request: Request, brand_id: int):

    return db.fetchOne(r'SELECT * FROM brands WHERE brand_id = %s', (brand_id,))


@inventory_router.get("/categories", response_class=JSONResponse)
async def list_categories(request: Request, user_perms: list[str] = Depends(user_permissions)):
    utils.check_user_permissions(
        user_perms,
        Permissions.inventory.manage_inventory,
        Permissions.inventory.view_inventory,
        Permissions.inventory.manage_categories,
        Permissions.inventory.view_categories
    )

    return db.fetchAll(r'SELECT * FROM categories')


@inventory_router.post("/categories/add", response_class=JSONResponse)
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


@inventory_router.post("/categories/update", response_class=JSONResponse)
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


@inventory_router.delete("/categories/delete/")
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


@inventory_router.get("/categories/{category_id}", response_class=JSONResponse)
async def fetch_category(request: Request, category_id: int, user_perms: list[str] = Depends(user_permissions)):
    utils.check_user_permissions(
        user_perms,
        Permissions.inventory.manage_inventory,
        Permissions.inventory.view_inventory,
        Permissions.inventory.manage_categories,
        Permissions.inventory.view_categories
    )

    return db.fetchOne(r'SELECT * FROM categories WHERE category_id = %s', (category_id,))


@inventory_router.get("/sizes", response_class=JSONResponse)
async def list_sizes(request: Request, user_perms: list[str] = Depends(user_permissions)):
    utils.check_user_permissions(
        user_perms,
        Permissions.inventory.manage_inventory,
        Permissions.inventory.view_inventory,
        Permissions.inventory.manage_sizes,
        Permissions.inventory.view_sizes
    )

    return db.fetchAll(r'SELECT * FROM sizes')


@inventory_router.post("/sizes/add", response_class=JSONResponse)
async def add_size(request: Request, size: float = Form(), sizing_system: str = Form(), user_perms: list[str] = Depends(user_permissions)):
    utils.check_user_permissions(
        user_perms,
        Permissions.inventory.manage_inventory,
        Permissions.inventory.manage_sizes,
    )

    try:

        if size < 0:
            raise DatabaseException("size cannot be negative.")

        if sizing_system.strip() == "":
            raise DatabaseException("sizing_system cannot be empty.")

        if not sizing_system.upper() in ["UK", "US", "EU"]:
            raise DatabaseException(
                "Invalid value for sizing_system.")

        db.commitOne(
            r'INSERT INTO sizes (size, sizing_system) VALUES (%s, %s)', (size, sizing_system))

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


@inventory_router.post("/sizes/update", response_class=JSONResponse)
async def edit_size(request: Request, size: Annotated[Size, Form()], user_perms: list[str] = Depends(user_permissions)):
    utils.check_user_permissions(
        user_perms,
        Permissions.inventory.manage_inventory,
        Permissions.inventory.manage_sizes,
    )

    try:

        if size.size <= 0:
            raise DatabaseException("size cannot be negative.")

        if size.sizing_system.strip() == "":
            raise DatabaseException("sizing_system cannot be empty.")

        if not size.sizing_system.upper() in ["UK", "US", "EU"]:
            raise DatabaseException(
                "Invalid value for sizing_system.")

        db.commitOne(
            r'UPDATE sizes SET size = %s, sizing_system = %s WHERE size_id = %s', (size.size, size.sizing_system, size.size_id))

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


@inventory_router.delete("/sizes/delete/")
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


@inventory_router.get("/sizes/{size_id}", response_class=JSONResponse)
async def fetch_size(request: Request, size_id: int, user_perms: list[str] = Depends(user_permissions)):
    utils.check_user_permissions(
        user_perms,
        Permissions.inventory.manage_inventory,
        Permissions.inventory.view_inventory,
        Permissions.inventory.manage_sizes,
        Permissions.inventory.view_sizes
    )

    return db.fetchOne(r'SELECT * FROM sizes WHERE size_id = %s', (size_id,))


@inventory_router.get("/variants", response_class=JSONResponse)
async def list_variants(request: Request, user_perms: list[str] = Depends(user_permissions)):
    utils.check_user_permissions(
        user_perms,
        Permissions.inventory.manage_inventory,
        Permissions.inventory.view_inventory,
        Permissions.inventory.manage_variants,
        Permissions.inventory.view_variants
    )

    return db.fetchAll(r'SELECT * FROM variants')


@inventory_router.post("/variants/add", response_class=JSONResponse)
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


@inventory_router.post("/variants/update", response_class=JSONResponse)
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


@inventory_router.delete("/variants/delete/")
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


@inventory_router.get("/variants/{variant_id}", response_class=JSONResponse)
async def fetch_variant(request: Request, variant_id: int, user_perms: list[str] = Depends(user_permissions)):
    utils.check_user_permissions(
        user_perms,
        Permissions.inventory.manage_inventory,
        Permissions.inventory.view_inventory,
        Permissions.inventory.manage_variants,
        Permissions.inventory.view_variants
    )

    return db.fetchOne(r'SELECT * FROM variants WHERE variant_id = %s', (variant_id,))
