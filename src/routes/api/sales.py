from fastapi import APIRouter, Request, Form
from fastapi.responses import JSONResponse

from ...includes import Database
from ...exceptions import DatabaseException
from ...models.sales import Sale, Return
from ...models.inventory import Variant

sales_router = APIRouter(prefix="/sales")

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
    try:
        cursor = db.commitOne(r'INSERT INTO sales (user_id, customer_name, total_amount, cash_received, change_amount) VALUES (%s, %s, %s, %s, %s)',
                              (user_id, customer_name, total_amount, cash_received, change_amount))

        sale_id = cursor.lastrowid

        for item in items.split(","):
            item = item.strip().split(":")
            variant_id, quantity = [int(it) for it in item]

            if result := db.fetchOne(r'SELECT product_id FROM variants WHERE variant_id = %s', (variant_id,)):
                product_id = result["product_id"]

                if product := db.fetchOne(r'SELECT product_price, markup FROM products WHERE product_id = %s', (product_id,)):
                    product_price = product["product_price"]
                    markup = product["markup"]
                    price = product_price * (1 + markup / 100) * quantity

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

        rowCount = db.commitOne(r'DELETE FROM sales WHERE sale_id = %s', (sale_id,)).rowcount

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
async def list_returns(request: Request):
    return db.fetchAll(r'SELECT * FROM returns')


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
        rowCount = db.commitOne(r'DELETE FROM returns WHERE return_id = %s', (return_id,)).rowcount

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
