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
            SELECT s.*, u.user_id, u.username, u.first_name, u.last_name,
                   CASE WHEN r.return_id IS NOT NULL THEN 'Returned' ELSE 'Active' END as status
            FROM sales s
            JOIN users u ON u.user_id = s.user_id
            LEFT JOIN returns r ON r.sale_id = s.sale_id
            WHERE s.sale_id = %s OR s.customer_name LIKE %s
            LIMIT %s OFFSET %s
            """,
            (query, f"%{query}%", limit, offset)
        )

    else:
        result = db.fetchAll(
            r"""
            SELECT s.*, u.user_id, u.username, u.first_name, u.last_name,
                   CASE WHEN r.return_id IS NOT NULL THEN 'Returned' ELSE 'Active' END as status
            FROM sales s
            JOIN users u ON u.user_id = s.user_id
            LEFT JOIN returns r ON r.sale_id = s.sale_id
            LIMIT %s OFFSET %s
            """,
            (limit, offset)
        )

    for sale in result:
        sale["sales_date"] = sale["sales_date"].isoformat()

    return JSONResponse({
        "result": result,
        "count": count,
        "pages": pages
    })


@sales_router.post("/add", response_class=JSONResponse)
async def add_sale(request: Request,
                   customer_name: str = Form(),
                   total_amount: float = Form(),
                   cash_received: float = Form(),
                   change_amount: float = Form(),
                   items: str = Form()
                   ):
    try:

        user_id = request.session["user_id"]

        if user_id <= 0:
            user_id = 1

        # Check stock availability first
        for item in items.split(","):
            item = item.strip().split(":")
            variant_id, quantity = [int(it) for it in item]

            if stock_result := db.fetchOne(r'SELECT variant_stock FROM variants WHERE variant_id = %s', (variant_id,)):
                if stock_result["variant_stock"] < quantity:
                    raise DatabaseException(
                        f"Insufficient stock for variant {variant_id}. Available: {stock_result['variant_stock']}, Requested: {quantity}")

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

                    db.commitOne(r'INSERT INTO sales_items (sale_id, variant_id, quantity, price) VALUES (%s, %s, %s, %s)',
                                 (sale_id, variant_id, quantity, price))

                    # Update stock
                    db.commitOne(r'UPDATE variants SET variant_stock = variant_stock - %s WHERE variant_id = %s',
                                 (quantity, variant_id))

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


@sales_router.get("/returns", response_class=JSONResponse)
async def list_returns(request: Request,
                       query: Annotated[Optional[str], Query()] = None,
                       page: Annotated[Optional[int], Query()] = 1,
                       limit: Annotated[Optional[int], Query()] = 10
                       ):

    count = db.fetchOne(r'SELECT COUNT(*) as count FROM returns')["count"]
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
            FROM returns r
            JOIN sales s ON s.sale_id = r.sale_id
            LIMIT %s OFFSET %s
            """,
            (limit, offset))

    for ret in result:
        ret["return_date"] = ret["return_date"].isoformat()
        ret["sales_date"] = ret["sales_date"].isoformat()

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


@sales_router.get("/returns/total", response_class=JSONResponse)
async def total_returns(request: Request):

    result = db.fetchOne(r"""
        SELECT
            COUNT(*) AS total_count,
            SUM(total_refund) AS total_refund
        FROM returns
    """)

    return JSONResponse(result)


@sales_router.get("/returns/{return_id}", response_class=JSONResponse)
async def fetch_return(request: Request, return_id: int):
    result = db.fetchOne(
        r'SELECT * FROM returns r JOIN sales s ON s.sale_id = r.sale_id WHERE return_id = %s', (return_id,))
    if result:
        result["return_date"] = result["return_date"].isoformat()
        result["sales_date"] = result["sales_date"].isoformat()
    return result


@sales_router.get("/monthly", response_class=JSONResponse)
async def monthly_sales(request: Request):

    # Get current year
    from datetime import datetime
    current_year = datetime.now().year

    # Get all months with sales data
    sales_data = db.fetchAll(r"""
        SELECT
            MONTH(sales_date) AS month_num,
            DATE_FORMAT(sales_date, '%M') AS month_name,
            SUM(total_amount) AS total_sales,
            COUNT(*) AS num_sales
        FROM sales
        WHERE YEAR(sales_date) = %s
        GROUP BY MONTH(sales_date), DATE_FORMAT(sales_date, '%M')
        ORDER BY month_num
    """, (current_year,))

    # Create complete list of 12 months
    month_names = ['January', 'February', 'March', 'April', 'May', 'June',
                   'July', 'August', 'September', 'October', 'November', 'December']

    result = []
    sales_dict = {item['month_num']: item for item in sales_data}

    for i in range(1, 13):
        if i in sales_dict:
            result.append(sales_dict[i])
        else:
            result.append({
                'month_num': i,
                'month_name': month_names[i-1],
                'total_sales': 0,
                'num_sales': 0
            })

    return JSONResponse(result)


@sales_router.get("/yearly", response_class=JSONResponse)
async def yearly_sales(request: Request):

    result = db.fetchAll(r"""
        SELECT
            YEAR(sales_date) AS year,
            SUM(total_amount) AS total_sales,
            COUNT(*) AS num_sales
        FROM sales
        GROUP BY YEAR(sales_date)
        ORDER BY year DESC
        LIMIT 5
    """)

    return JSONResponse(result)


@sales_router.get("/total", response_class=JSONResponse)
async def total_sales(request: Request):

    result = db.fetchOne(r"""
        SELECT
            SUM(total_amount) AS total_amount,
            COUNT(*) AS total_count
        FROM sales
    """)

    return JSONResponse(result)


@sales_router.get("/{sale_id}", response_class=JSONResponse)
async def fetch_sale(request: Request, sale_id: int):

    result = db.fetchOne(
        r"""
        SELECT s.*, u.username, u.first_name, u.last_name,
               CASE WHEN r.return_id IS NOT NULL THEN 'Returned' ELSE 'Active' END as status
        FROM sales s
        JOIN users u ON u.user_id = s.user_id
        LEFT JOIN returns r ON r.sale_id = s.sale_id
        WHERE s.sale_id = %s
        """,
        (sale_id,)
    )

    if result:
        result["sales_date"] = result["sales_date"].isoformat()

    return result


@sales_router.get("/{sale_id}/items", response_class=JSONResponse)
async def list_sales_items(request: Request, sale_id: int):

    return db.fetchAll(r'SELECT * FROM sales_items WHERE sale_id = %s', (sale_id,))
