from typing import Optional

from fastapi import APIRouter, Request, Form, Query
from fastapi.responses import JSONResponse

from ...includes import Database
from ...models.sales import Sale
from ...models.inventory import Variant

sales_router = APIRouter(prefix="/api/sales")

db = Database()


@sales_router.get("/", response_class=JSONResponse)
async def list_sales(request: Request):
    return db.fetchAll(r'SELECT * FROM sales')


@sales_router.post("/add", response_class=JSONResponse)
async def add_sale(request: Request,
                   user_id: int = Form(),
                   customer_name: str = Form(),
                   total_amount: float = Form(),
                   cash_received: float = Form(),
                   change_amount: float = Form(),
                   items: str = Form()
                   ):

    # items_tuple = tuple((item,) for item in items)

    print(items)


@sales_router.get("/{sale_id}", response_class=JSONResponse)
async def fetch_sale(request: Request, sale_id: Optional[int] = None):

    if sale_id is None:
        return []

    return db.fetchAll(r'SELECT * FROM sales WHERE sales_id = %s', (sale_id,))


@sales_router.get("/{sale_id}/items", response_class=JSONResponse)
async def list_sales_items(request: Request, sale_id: int):

    if sale_id is None:
        return []

    return db.fetchAll(r'SELECT * FROM sales_items WHERE sale_id = %s', (sale_id,))


@sales_router.get("/returns", response_class=JSONResponse)
async def list_returns(request: Request):
    return db.fetchAll(r'SELECT * FROM returns')


@sales_router.get("/returns/{return_id}", response_class=JSONResponse)
async def fetch_return(request: Request, return_id: Optional[int] = None):
    if return_id is None:
        return []

    return db.fetchAll(r'SELECT * FROM returns WHERE return_id = %s', (return_id,))
