import math
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Form, Query, Request
from fastapi.responses import JSONResponse

from .... import utils
from ....depedencies import is_authenticated, user_permissions
from ....exceptions import DatabaseException
from ....helpers import Database
from ....models.inventory import Variant
from ....utils import Permissions

variants_router = APIRouter(
    prefix="/variants", dependencies=[Depends(is_authenticated)])

db = Database()


@variants_router.get("", response_class=JSONResponse)
async def list_variants(request: Request,
                        query: Annotated[Optional[str], Query()] = None,
                        page: Annotated[Optional[int], Query()] = 1,
                        limit: Annotated[Optional[int], Query()] = 10,
                        low_stock: Annotated[Optional[str], Query()] = None):

    # First, get the shoes for the current page
    base_query = """
        SELECT s.*, b.brand_name
        FROM shoes s
        JOIN brands b ON b.brand_id = s.brand_id
    """
    count_query = "SELECT COUNT(*) as count FROM shoes s JOIN brands b ON b.brand_id = s.brand_id"
    where_clauses = []
    params = []

    if low_stock == '1':
        where_clauses.append("EXISTS (SELECT 1 FROM variants v WHERE v.shoe_id = s.shoe_id AND v.variant_stock <= 20)")
    
    if query:
        where_clauses.append("(s.shoe_id = %s OR s.shoe_name LIKE %s OR b.brand_name LIKE %s)")
        params.extend([query, f"%{query}%", f"%{query}%"])

    if where_clauses:
        where_sql = " WHERE " + " AND ".join(where_clauses)
        base_query += where_sql
        count_query += where_sql

    shoe_count = db.fetchOne(count_query, params)["count"] if params else db.fetchOne(count_query)["count"]
    shoe_pages = math.ceil(shoe_count / limit)
    shoe_offset = (page - 1) * limit

    shoes = db.fetchAll(base_query + " LIMIT %s OFFSET %s", params + [limit, shoe_offset])

    # For each shoe, get its variants
    result = []
    for shoe in shoes:
        shoe_id = shoe["shoe_id"]
        variant_query = """
            SELECT v.*, sz.us_size, sz.uk_size, sz.eu_size
            FROM variants v
            JOIN sizes sz ON sz.size_id = v.size_id
            WHERE v.shoe_id = %s
        """
        params = [shoe_id]
        if low_stock == '1':
            variant_query += " AND v.variant_stock <= 20"
        variant_query += " ORDER BY sz.us_size"
        variants = db.fetchAll(variant_query, params)
        shoe["variants"] = variants
        shoe["created_at"] = shoe["created_at"].isoformat()
        shoe["first_sale_at"] = shoe["first_sale_at"].isoformat()

        result.append(shoe)

    return JSONResponse({
        "result": result,
        "count": shoe_count,
        "pages": shoe_pages
    })


@variants_router.post("/add", response_class=JSONResponse)
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

        if _ := db.fetchOne(r'SELECT * FROM variants WHERE size_id = %s AND shoe_id = %s', (size_id, shoe_id)):
            return JSONResponse({
                "success": False,
                "message": "Variant already exists."
            }, status_code=201)

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


@variants_router.post("/update", response_class=JSONResponse)
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

        if _ := db.fetchOne(r'SELECT * FROM variants WHERE size_id = %s AND shoe_id = %s', (variant.size_id, variant.shoe_id)):
            return JSONResponse({
                "success": False,
                "message": "Variant already exists."
            }, status_code=201)

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


@variants_router.delete("/delete/")
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


@variants_router.get("/low-stock", response_class=JSONResponse)
async def low_stock_variants(request: Request, threshold: int = 20, user_perms: list[str] = Depends(user_permissions)):
    utils.check_user_permissions(
        user_perms,
        Permissions.inventory.view_inventory,
        Permissions.inventory.view_variants
    )

    # Get total count
    total = db.fetchOne(r"""
        SELECT COUNT(*) as count
        FROM variants v
        WHERE v.variant_stock <= %s
    """, (threshold,))["count"]

    result = db.fetchAll(r"""
        SELECT
            v.variant_id,
            s.shoe_id,
            s.shoe_name,
            sz.us_size,
            sz.uk_size,
            sz.eu_size,
            v.variant_stock
        FROM variants v
        JOIN shoes s ON v.shoe_id = s.shoe_id
        JOIN sizes sz ON v.size_id = sz.size_id
        WHERE v.variant_stock <= %s
        ORDER BY v.variant_stock ASC
        LIMIT 20
    """, (threshold,))

    return JSONResponse({"data": result, "total": total})


@variants_router.get("/{variant_id}", response_class=JSONResponse)
async def fetch_variant(request: Request, variant_id: int, user_perms: list[str] = Depends(user_permissions)):
    utils.check_user_permissions(
        user_perms,
        Permissions.inventory.manage_inventory,
        Permissions.inventory.view_inventory,
        Permissions.inventory.manage_variants,
        Permissions.inventory.view_variants
    )

    return db.fetchOne(r'SELECT * FROM variants WHERE variant_id = %s', (variant_id,))
