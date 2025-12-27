
from typing import Optional, Annotated

import os
import shutil
from io import BytesIO
from PIL import Image

from fastapi import APIRouter, Request, Form, File, UploadFile, Depends
from fastapi.responses import JSONResponse

from ... import utils
from ...depedencies import is_authenticated, user_permissions
from ...includes import Database
from ...models.inventory import (
    Brand,
    Category,
    Product,
    Size,
    Variant
)
from ...exceptions import DatabaseException

inventory_router = APIRouter(prefix="/inventory",
                             dependencies=[Depends(is_authenticated)])

db = Database()


@inventory_router.get("/products", response_class=JSONResponse)
async def list_products(request: Request, user_perms: list[str] = Depends(user_permissions)):

    utils.check_user_permissions(user_perms, "view_invetory", "manage_inventory")

    return db.fetchAll(r"SELECT * FROM products")


@inventory_router.post("/products/add", response_class=JSONResponse)
async def add_product(request: Request,
                      file: UploadFile | None = File(None),
                      product_name: str = Form(),
                      brand_id: int = Form(),
                      category_id: int = Form(),
                      markup: int = Form(),
                      product_price: float = Form(),
                      first_sale_at: str = Form()):
    try:
        if product_name.strip() == "":
            raise DatabaseException("product_name is empty.")

        cursor = db.commitOne(
            r'INSERT INTO products (product_name, brand_id, category_id, markup, product_price, first_sale_at) VALUES (%s, %s, %s, %s, %s, %s)',
            (product_name, brand_id, category_id,
             markup, product_price, first_sale_at)
        )

        product_id = cursor.lastrowid

        # Handle image upload
        if file is not None:
            if not file.content_type or not file.content_type.startswith("image"):
                return JSONResponse(
                    {"success": False,
                        "message": f"Uploaded file ({file.content_type}) is not an image."},
                    status_code=415
                )

            # Create product directory
            from ...Settings import Settings
            product_dir = os.path.join(
                Settings.products.path, f"product-{product_id:05d}")
            os.makedirs(product_dir, exist_ok=True)

            # Process image
            image = Image.open(file.file)
            if image.mode in ('RGBA', 'P'):
                image = image.convert("RGB")
            image = image.resize(
                (Settings.products.size, Settings.products.size))

            # Save image
            buffer = BytesIO()
            image.save(buffer, format="JPEG",
                       quality=Settings.products.quality)
            buffer.seek(0)

            image_path = os.path.join(
                product_dir, f"product-{product_id:05d}.jpeg")
            with open(image_path, "wb") as f:
                f.write(buffer.read())
        else:
            # Copy default image
            from ...Settings import Settings
            product_dir = os.path.join(
                Settings.products.path, f"product-{product_id:05d}")
            os.makedirs(product_dir, exist_ok=True)
            shutil.copy(Settings.products.default, os.path.join(
                product_dir, f"product-{product_id:05d}.jpeg"))

        return JSONResponse({
            "success": True,
            "message": "Successfully Added Product."
        }, status_code=201)
    except Exception as e:
        return JSONResponse({
            "success": False,
            "message": f"{e}"
        },
            status_code=400
        )


@inventory_router.post("/products/update", response_class=JSONResponse)
async def edit_product(request: Request, product: Annotated[Product, Form()]):
    try:

        if product.brand_id < 0:
            raise DatabaseException("brand_id cannot be negative")

        if product.product_name.strip() == "":
            raise DatabaseException("brand_name is empty.")

        db.commitOne(
            r'UPDATE products SET product_name = %s, brand_id = %s, category_id = %s, markup = %s, product_price = %s, first_sale_at = %s  WHERE product_id = %s',
            (product.product_name, product.brand_id, product.category_id, product.markup,
             product.product_price, product.first_sale_at, product.product_id)
        )

        return {
            "success": True,
            "message": "Successfully Updated Product."
        }
    except Exception as e:
        return JSONResponse({
            "success": False,
            "message": f"{e}"
        },
            status_code=400
        )


@inventory_router.delete("/products/delete/")
async def delete_product(request: Request, product_id: int):
    try:
        rowCount = db.commitOne(
            r'DELETE FROM products WHERE product_id = %s', (product_id,)).rowcount

        if rowCount <= 0:
            raise DatabaseException("product_id doesn't exist.")

        return {
            "success": True,
            "message": "Successfully Deleted Product."
        }
    except Exception as e:
        return JSONResponse({
            "success": False,
            "message": f"{e}"
        },
            status_code=400
        )


@inventory_router.get("/products/popular", response_class=JSONResponse)
async def list_popular(request: Request, limit: int = 10):

    return db.fetchAll(r"""
            SELECT
                p.product_id,
                p.product_name,
                SUM(si.quantity) AS total_quantity,
                SUM(si.price) AS total_revenue
            FROM
                sales_items si
            JOIN variants v ON
                si.variant_id = v.variant_id
            JOIN products p ON
                v.product_id = p.product_id
            GROUP BY
                p.product_id,
                p.product_name
            ORDER BY
                total_quantity
            DESC
            LIMIT %s;
               """, (limit,))


@inventory_router.get("/products/{product_id}", response_class=JSONResponse)
async def fetch_product(request: Request, product_id: int):

    return db.fetchOne(r'SELECT * FROM products WHERE product_id = %s', (product_id,))


@inventory_router.get("/brands", response_class=JSONResponse)
async def list_brands(request: Request):
    return db.fetchAll(r'SELECT * FROM brands')


@inventory_router.post("/brands/add", response_class=JSONResponse)
async def add_brand(request: Request, brand_name: str = Form()):
    try:

        if brand_name.strip() == "":
            raise DatabaseException("brand_name is empty.")

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
async def edit_brand(request: Request, brand: Annotated[Brand, Form()]):
    try:

        if brand.brand_id < 0:
            raise DatabaseException("brand_id cannot be negative")

        if brand.brand_name.strip() == "":
            raise DatabaseException("brand_name is empty.")

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


@inventory_router.delete("/brands/delete/")
async def delete_brand(request: Request, brand_id: int):
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
async def list_categories(request: Request):
    return db.fetchAll(r'SELECT * FROM categories')


@inventory_router.post("/categories/add", response_class=JSONResponse)
async def add_category(request: Request, category_name: str = Form()):
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
async def edit_category(request: Request, category: Annotated[Category, Form()]):
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
async def delete_category(request: Request, category_id: int):
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
async def fetch_category(request: Request, category_id: int):
    return db.fetchOne(r'SELECT * FROM categories WHERE category_id = %s', (category_id,))


@inventory_router.get("/sizes", response_class=JSONResponse)
async def list_sizes(request: Request):
    return db.fetchAll(r'SELECT * FROM sizes')


@inventory_router.post("/sizes/add", response_class=JSONResponse)
async def add_size(request: Request, size: float = Form(), sizing_system: str = Form()):
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
async def edit_size(request: Request, size: Annotated[Size, Form()]):
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
async def delete_size(request: Request, size_id: int):
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
async def fetch_size(request: Request, size_id: int):
    return db.fetchOne(r'SELECT * FROM sizes WHERE size_id = %s', (size_id,))


@inventory_router.get("/variants", response_class=JSONResponse)
async def list_variants(request: Request):
    return db.fetchAll(r'SELECT * FROM variants')


@inventory_router.post("/variants/add", response_class=JSONResponse)
async def add_variant(request: Request,
                      product_id: int = Form(),
                      size_id: int = Form(),
                      variant_stock: int = Form()
                      ):
    try:

        if product_id is None or product_id < 0:
            raise DatabaseException("product_id is invalid.")

        if size_id is None or size_id < 0:
            raise DatabaseException("size_id is invalid.")

        if variant_stock is None or variant_stock < 0:
            raise DatabaseException("variant_stock is invalid.")

        db.commitOne(
            r'INSERT INTO variants (product_id, size_id, variant_stock) VALUES (%s, %s, %s)', (product_id, size_id, variant_stock))

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
async def edit_variant(request: Request, variant: Annotated[Variant, Form()]):
    try:

        if variant.variant_id is None or variant.variant_id < 0:
            raise DatabaseException("variant_id is invalid.")

        if variant.product_id is None or variant.product_id < 0:
            raise DatabaseException("product_id is invalid.")

        if variant.size_id is None or variant.size_id < 0:
            raise DatabaseException("size_id is invalid.")

        if variant.variant_stock is None or variant.variant_stock < 0:
            raise DatabaseException("variant_stock is invalid.")

        db.commitOne(
            r'UPDATE variants SET product_id = %s, size_id = %s, variant_stock = %s WHERE variant_id = %s',
            (variant.product_id, variant.size_id,
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
async def delete_variant(request: Request, variant_id: int):
    try:
        rowCount = db.commitOne(
            r'DELETE FROM variants WHERE variant_id = %s', (variant_id,)).rowcount

        if rowCount <= 0:
            raise DatabaseException("size_id doesn't exist.")

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
async def fetch_variant(request: Request, variant_id: int):
    return db.fetchOne(r'SELECT * FROM variants WHERE variant_id = %s', (variant_id,))
