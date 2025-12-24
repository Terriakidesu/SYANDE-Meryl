
from typing import Optional

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from ...includes import Database

inventory_router = APIRouter(prefix="/api/inventory")

db = Database()


@inventory_router.get("/", response_class=JSONResponse)
async def list_items(request: Request):
    return db.fetchAll(r"SELECT * FROM products")


@inventory_router.get("/{product_id}", response_class=JSONResponse)
async def fetch_item(request: Request, product_id: Optional[int] = None):

    if product_id is None:
        return []

    return db.fetchAll(r"SELECT * FROM products WHERE product_id = %s", (product_id,))
