
from typing import Optional, Annotated

from fastapi import APIRouter, Request, Form
from fastapi.responses import JSONResponse

from ...includes import Database
from ...models.inventory import (
    Brand,
    Category,
    Product,
    ProductForm,
    Size
)
from ...exceptions import (
    DatabaseDeleteException,
    DatabaseInsertionException,
    DatabaseException
)

inventory_router = APIRouter(prefix="/api/inventory")

db = Database()


@inventory_router.get("/products", response_class=JSONResponse)
async def list_products(request: Request):
    return db.fetchAll(r"SELECT * FROM products")


@inventory_router.post("/products/add", response_class=JSONResponse)
async def add_product(request: Request, product: Annotated[ProductForm, Form()]):
    try:

        if product.product_name.strip() == "":
            raise DatabaseInsertionException("product_name is empty.")

        db.commitOne(
            r'INSERT INTO products (prodct_name, brand_id, category_id, product_price, first_sale_at) VALUES (%s, %s, %s, %s, %s)',
            (product.product_name, product.brand_id, product.category_id,
             product.product_price, product.first_sale_at)
        )

        return {
            "success": True,
            "message": f"Successfully Added Product."
        }
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
            raise DatabaseInsertionException("brand_name is empty.")

        db.commitOne(
            r'UPDATE products SET product_name = %s, brand_id = %s, category_id = %s, product_price = %s, first_sale_at = %s  WHERE product_id = %s',
            (product.product_name, product.brand_id, product.category_id,
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
            raise DatabaseDeleteException("brand_id doesn't exist.")

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


@inventory_router.get("/products/{product_id}", response_class=JSONResponse)
async def fetch_product(request: Request, product_id: Optional[int] = None):

    return db.fetchOne(r"SELECT * FROM products WHERE product_id = %s", (product_id,))


@inventory_router.get("/brands", response_class=JSONResponse)
async def list_brands(request: Request):
    return db.fetchAll(r'SELECT * FROM brands')


@inventory_router.post("/brands/add", response_class=JSONResponse)
async def add_brand(request: Request, brand_name: str = Form()):
    try:

        if brand_name.strip() == "":
            raise DatabaseInsertionException("brand_name is empty.")

        db.commitOne(
            r'INSERT INTO brands (brand_name) VALUES (%s)', (brand_name,))

        return {
            "success": True,
            "message": f"Successfully Added Brand."
        }
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
            raise DatabaseInsertionException("brand_name is empty.")

        db.commitOne(
            r'UPDATE brands SET brand_name = %s WHERE brand_id = %s', (brand.brand_name, brand.brand_id))

        return {
            "success": True,
            "message": f"Successfully Updated Product."
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
            raise DatabaseDeleteException("brand_id doesn't exist.")

        return {
            "success": True,
            "message": f"Successfully Deleted Product."
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
    return db.fetchAll(r'SELECT * FROM brands WHERE brand_id = %s', (brand_id,))


@inventory_router.get("/categories", response_class=JSONResponse)
async def list_categories(request: Request):
    return db.fetchAll(r'SELECT * FROM categories')


@inventory_router.post("/categories/add", response_class=JSONResponse)
async def add_category(request: Request, category_name: str = Form()):
    try:

        if category_name.strip() == "":
            raise DatabaseInsertionException("category_name is empty.")

        db.commitOne(
            r'INSERT INTO categories (category_name) VALUES (%s)', (category_name,))

        return {
            "success": True,
            "message": f"Successfully Added Category."
        }
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
            raise DatabaseInsertionException("category_name is empty.")

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
            raise DatabaseDeleteException("category_id doesn't exist.")

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
    return db.fetchAll(r'SELECT * FROM category WHERE category_id = %s', (category_id,))


@inventory_router.get("/sizes", response_class=JSONResponse)
async def list_sizes(request: Request):
    return db.fetchAll(r'SELECT * FROM sizes')


@inventory_router.post("/sizes/add", response_class=JSONResponse)
async def add_size(request: Request, size: float = Form(), sizing_system: str = Form()):
    try:

        if size <= 0:
            raise DatabaseInsertionException("size cannot be negative.")

        if sizing_system.strip() == "":
            raise DatabaseInsertionException("sizing_system cannot be empty.")

        if not sizing_system.upper() in ["UK", "US", "EU"]:
            raise DatabaseInsertionException(
                "Invalid value for sizing_system.")

        db.commitOne(
            r'INSERT INTO sizes (size, sizing_system) VALUES (%s, %s)', (size, sizing_system))

        return {
            "success": True,
            "message": f"Successfully Added Size."
        }
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
            raise DatabaseInsertionException("size cannot be negative.")

        if size.sizing_system.strip() == "":
            raise DatabaseInsertionException("sizing_system cannot be empty.")

        if not size.sizing_system.upper() in ["UK", "US", "EU"]:
            raise DatabaseInsertionException(
                "Invalid value for sizing_system.")

        db.commitOne(
            r'UPDATE sizes SET size = %s, sizing_system WHERE size_id = %s', (size.size, size.sizing_system, size.size_id))

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
            raise DatabaseDeleteException("size_id doesn't exist.")

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
    return db.fetchAll(r'SELECT * FROM sizes WHERE size_id = %s', (size_id,))
