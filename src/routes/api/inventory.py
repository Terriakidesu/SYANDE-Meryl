
from typing import Optional

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from ...includes import Database

inventory_router = APIRouter(prefix="/api/inventory")

db = Database()


@inventory_router.get("/products", response_class=JSONResponse)
async def list_products(request: Request):
    return db.fetchAll(r"SELECT * FROM products")


@inventory_router.get("/products/{product_id}", response_class=JSONResponse)
async def fetch_product(request: Request, product_id: Optional[int] = None):

    return db.fetchOne(r"SELECT * FROM products WHERE product_id = %s", (product_id,))


@inventory_router.get("/brands", response_class=JSONResponse)
async def list_brands(request: Request):
    return db.fetchAll(r'SELECT * FROM brands')


@inventory_router.get("/brands/{brand_id}", response_class=JSONResponse)
async def fetch_brand(request: Request, brand_id: int):
    return db.fetchAll(r'SELECT * FROM brands WHERE brand_id = %s', (brand_id,))


@inventory_router.get("/categories", response_class=JSONResponse)
async def list_categories(request: Request):
    return db.fetchAll(r'SELECT * FROM categories')


@inventory_router.get("/categories/{category_id}", response_class=JSONResponse)
async def fetch_category(request: Request, category_id: int):
    return db.fetchAll(r'SELECT * FROM category WHERE category_id = %s', (category_id,))
