import math
from typing import Annotated, Optional

from fastapi import APIRouter, Form, Query, Request
from fastapi.responses import JSONResponse

from ...exceptions import DatabaseException
from ...helpers import Database
from ...models.inventory import Variant
from ...models.sales import Return, Sale

sales_router = APIRouter(prefix="/sales")

db = Database()


@sales_router.get("/", response_class=JSONResponse)
async def list_sales(request: Request,
                     query: Annotated[Optional[str], Query()] = None,
                     page: Annotated[Optional[int], Query()] = 1,
                     limit: Annotated[Optional[int], Query()] = 10
                     ):

    count = db.fetchOne(r'SELECT COUNT(*) as count FROM sales')["count"]
    pages = math.ceil(count / limit)
    offset = (page - 1) * limit

    if query:
        result = db.fetchAll(
            r"""
            SELECT * 
            FROM sales s 
            JOIN users u ON u.user_id = s.user_id 
            WHERE s.sales_id = %s OR s.customer_name LIKE %s 
            LIMIT %s OFFSET %s
            """,
            (query, f"%{query}%", limit, offset)
        )

        return JSONResponse({
            "result": result,
            "count": count,
            "pages": pages
        })

    result = db.fetchAll(
        r"""
        SELECT * 
        FROM sales s 
        JOIN users u ON u.user_id = s.user_id 
        LIMIT %s OFFSET %s
        """,
        (limit, offset)
    )

    return JSONResponse({
        "result": result,
        "count": count,
        "pages": pages
    })


@sales_router.post("/add", response_class=JSONResponse)
async def add_sale(request: Request,
                   user_id: int = Form(),
                   customer_name: str = Form(),
                   total_amount: float = Form(),
                   cash_received: float = Form(),
                   change_amount: float = Form(),
                   items: str = Form()
                   ):
    try:
        cursor = db.commitOne(r'INSERT INTO sales (user_id, customer_name, total_amount, cash_received, change_amount) VALUES (%s, %s, %s, %s, %s)',
                              (user_id, customer_name, total_amount, cash_received, change_amount))

        sale_id = cursor.lastrowid

        for item in items.split(","):
            item = item.strip().split(":")
            variant_id, quantity = [int(it) for it in item]

            if result := db.fetchOne(r'SELECT shoe_id FROM variants WHERE variant_id = %s', (variant_id,)):
                shoe_id = result["shoe_id"]

                if shoe := db.fetchOne(r'SELECT shoe_price, markup FROM shoes WHERE shoe_id = %s', (shoe_id,)):
                    shoe_price = shoe["shoe_price"]
                    markup = shoe["markup"]
                    price = shoe_price * (1 + markup / 100) * quantity

                    db.commitOne(r'INSERT INTO sales_items (sale_id, variant_id, markup, quantity, price) VALUES (%s, %s, %s, %s, %s)',
                                 (sale_id, variant_id, markup, quantity, price))

        return JSONResponse({
            "success": True,
            "message": "Sale added successfully"
        }, status_code=201)
    except Exception as e:
        return JSONResponse({
            "success": False,
            "message": f"{e}"
        },
            status_code=400
        )


@sales_router.post("/update", response_class=JSONResponse)
async def update_sale(request: Request,
                      sale_id: int = Form(),
                      user_id: int = Form(),
                      customer_name: str = Form(),
                      total_amount: float = Form(),
                      cash_received: float = Form(),
                      change_amount: float = Form()):
    try:
        if sale_id < 0:
            raise DatabaseException("sale_id cannot be negative")

        db.commitOne(r'UPDATE sales SET user_id = %s, customer_name = %s, total_amount = %s, cash_received = %s, change_amount = %s WHERE sale_id = %s',
                     (user_id, customer_name, total_amount, cash_received, change_amount, sale_id))

        return {
            "success": True,
            "message": "Sale updated successfully"
        }
    except Exception as e:
        return JSONResponse({
            "success": False,
            "message": f"{e}"
        },
            status_code=400
        )


@sales_router.delete("/delete/{sale_id}", response_class=JSONResponse)
async def delete_sale(request: Request, sale_id: int):
    try:
        # Delete sales_items first
        db.commitOne(r'DELETE FROM sales_items WHERE sale_id = %s', (sale_id,))

        rowCount = db.commitOne(
            r'DELETE FROM sales WHERE sale_id = %s', (sale_id,)).rowcount

        if rowCount <= 0:
            raise DatabaseException("sale_id doesn't exist.")

        return {
            "success": True,
            "message": "Sale deleted successfully"
        }
    except Exception as e:
        return JSONResponse({
            "success": False,
            "message": f"{e}"
        },
            status_code=400
        )


@sales_router.get("/{sale_id}", response_class=JSONResponse)
async def fetch_sale(request: Request, sale_id: int):

    return db.fetchOne(r'SELECT * FROM sales WHERE sale_id = %s', (sale_id,))


@sales_router.get("/{sale_id}/items", response_class=JSONResponse)
async def list_sales_items(request: Request, sale_id: int):

    return db.fetchAll(r'SELECT * FROM sales_items WHERE sale_id = %s', (sale_id,))


@sales_router.get("/returns", response_class=JSONResponse)
async def list_returns(request: Request,
                       query: Annotated[Optional[str], Query()] = None,
                       page: Annotated[Optional[int], Query()] = 1,
                       limit: Annotated[Optional[int], Query()] = 10
                       ):

    count = db.fetchOne(r'SELECT COUNT(*) as count FROM sales')["count"]
    pages = math.ceil(count / limit)
    offset = (page - 1) * limit

    if query:
        result = db.fetchAll(
            r"""
            SELECT * 
            FROM returns r
            JOIN sales s ON s.sale_id = r.sale_id
            WHERE s.sale_id = % OR r.return_id = %s OR s.customer_name = %s
            LIMIT %s OFFSET %s
            """,
            (query, query, f"{query}%", limit, offset))
    else:
        result = db.fetchAll(
            r"""
            SELECT * 
            FROM returns
            JOIN sales s ON s.sale_id = r.sale_id
            LIMIT %s OFFSET %s
            """,
            (limit, offset))

    return JSONResponse({
        "result": result,
        "count": count,
        "pages": pages
    })


@sales_router.post("/returns/add", response_class=JSONResponse)
async def add_return(request: Request,
                     sale_id: int = Form(),
                     customer_name: str = Form(),
                     return_reason: str = Form(),
                     total_refund: float = Form()):
    try:
        db.commitOne(r'INSERT INTO returns (sale_id, customer_name, return_reason, total_refund) VALUES (%s, %s, %s, %s)',
                     (sale_id, customer_name, return_reason, total_refund))

        return JSONResponse({
            "success": True,
            "message": "Return added successfully"
        }, status_code=201)
    except Exception as e:
        return JSONResponse({
            "success": False,
            "message": f"{e}"
        },
            status_code=400
        )


@sales_router.post("/returns/update", response_class=JSONResponse)
async def update_return(request: Request,
                        return_id: int = Form(),
                        sale_id: int = Form(),
                        customer_name: str = Form(),
                        return_reason: str = Form(),
                        total_refund: float = Form()):
    try:
        if return_id < 0:
            raise DatabaseException("return_id cannot be negative")

        db.commitOne(r'UPDATE returns SET sale_id = %s, customer_name = %s, return_reason = %s, total_refund = %s WHERE return_id = %s',
                     (sale_id, customer_name, return_reason, total_refund, return_id))

        return {
            "success": True,
            "message": "Return updated successfully"
        }
    except Exception as e:
        return JSONResponse({
            "success": False,
            "message": f"{e}"
        },
            status_code=400
        )


@sales_router.delete("/returns/delete/{return_id}", response_class=JSONResponse)
async def delete_return(request: Request, return_id: int):
    try:
        rowCount = db.commitOne(
            r'DELETE FROM returns WHERE return_id = %s', (return_id,)).rowcount

        if rowCount <= 0:
            raise DatabaseException("return_id doesn't exist.")

        return {
            "success": True,
            "message": "Return deleted successfully"
        }
    except Exception as e:
        return JSONResponse({
            "success": False,
            "message": f"{e}"
        },
            status_code=400
        )


@sales_router.get("/returns/{return_id}", response_class=JSONResponse)
async def fetch_return(request: Request, return_id: int):
    return db.fetchOne(r'SELECT * FROM returns WHERE return_id = %s', (return_id,))
