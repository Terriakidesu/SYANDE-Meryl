import math
import datetime
import os
import shutil
from io import BytesIO
from typing import Annotated, Optional, List

from fastapi import APIRouter, Depends, File, Form, Query, Request, UploadFile
from fastapi.responses import JSONResponse
from PIL import Image

from .... import utils
from ....depedencies import is_authenticated, user_permissions
from ....exceptions import DatabaseException
from ....helpers import Database
from ....models.inventory import Shoe
from ....utils import Permissions

shoes_router = APIRouter(
    prefix="/shoes", dependencies=[Depends(is_authenticated)])

db = Database()


@shoes_router.get("", response_class=JSONResponse)
async def list_shoes(request: Request,
                     query: Annotated[Optional[str], Query()] = None,
                     page: Annotated[Optional[int], Query()] = 1,
                     limit: Annotated[Optional[int], Query()] = 10
                     ):

    count = db.fetchOne(r'SELECT COUNT(*) as count FROM shoes')["count"]
    pages = math.ceil(count / limit)
    offset = (page - 1) * limit

    if query:
        result = db.fetchAll(
            r'SELECT * FROM shoes WHERE shoe_id = %s OR shoe_name LIKE %s LIMIT %s OFFSET %s', (query, f"%{query}%", limit, offset))

        return JSONResponse({
            "result": result,
            "count": count,
            "pages": pages
        })

    result = db.fetchAll(
        r'SELECT * FROM shoes LIMIT %s OFFSET %s', (limit, offset))

    return JSONResponse({
        "result": result,
        "count": count,
        "pages": pages
    })


@shoes_router.get("/all", response_class=JSONResponse)
async def list_shoes(request: Request,
                     query: Annotated[Optional[str], Query()] = None,
                     brand_ids: Annotated[Optional[str], Query()] = None,
                     category_ids: Annotated[Optional[str], Query()] = None,
                     demographic_ids: Annotated[Optional[str], Query()] = None,
                     page: Annotated[Optional[int], Query()] = 1,
                     limit: Annotated[Optional[int], Query()] = 10
                     ):

    # Build WHERE conditions
    where_conditions = []
    params = []

    if query:
        where_conditions.append("(s.shoe_id = %s OR s.shoe_name LIKE %s)")
        params.extend([query, f"%{query}%"])

    if brand_ids:
        brand_list = [int(bid.strip()) for bid in brand_ids.split(',') if bid.strip()]
        if brand_list:
            placeholders = ','.join(['%s'] * len(brand_list))
            where_conditions.append(f"s.brand_id IN ({placeholders})")
            params.extend(brand_list)

    if category_ids:
        category_list = [int(cid.strip()) for cid in category_ids.split(',') if cid.strip()]
        if category_list:
            placeholders = ','.join(['%s'] * len(category_list))
            where_conditions.append(f"EXISTS (SELECT 1 FROM shoe_categories sc WHERE sc.shoe_id = s.shoe_id AND sc.category_id IN ({placeholders}))")
            params.extend(category_list)

    if demographic_ids:
        demographic_list = [int(did.strip()) for did in demographic_ids.split(',') if did.strip()]
        if demographic_list:
            for demo_id in demographic_list:
                where_conditions.append(f"EXISTS (SELECT 1 FROM shoe_demographics sd WHERE sd.shoe_id = s.shoe_id AND sd.demographic_id = %s)")
                params.append(demo_id)

    where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"

    # Count query
    count_query = f"""
    SELECT COUNT(*) as count
    FROM shoes s
    JOIN brands b ON b.brand_id = s.brand_id
    WHERE {where_clause}
    """
    count = db.fetchOne(count_query, tuple(params))["count"]
    pages = math.ceil(count / limit) if count > 0 else 1
    offset = (page - 1) * limit

    # Data query
    data_query = f"""
    SELECT *
    FROM shoes s
    JOIN brands b ON b.brand_id = s.brand_id
    WHERE {where_clause}
    LIMIT %s OFFSET %s
    """
    params.extend([limit, offset])
    result = db.fetchAll(data_query, tuple(params))

    for shoe in result:
        shoe_id = shoe["shoe_id"]

        shoe["created_at"] = shoe["created_at"].isoformat()
        shoe["first_sale_at"] = shoe["first_sale_at"].isoformat()

        shoe["categories"] = db.fetchAll(
            r"""
            SELECT c.*
            FROM shoe_categories sc
            JOIN categories c ON sc.category_id = c.category_id
            WHERE sc.shoe_id = %s """, (shoe_id,)
        )

        shoe["demographics"] = db.fetchAll(
            r"""
            SELECT d.*
            FROM shoe_demographics sd
            JOIN demographics d ON sd.demographic_id = d.demographic_id
            WHERE sd.shoe_id = %s """, (shoe_id,)
        )

        shoe["variants"] = db.fetchAll(
            r"""
            SELECT v.*, sz.us_size, sz.uk_size, sz.eu_size
            FROM variants v
            JOIN sizes sz ON sz.size_id = v.size_id
            WHERE v.shoe_id = %s
            ORDER BY sz.us_size
            """, (shoe_id,))

    return JSONResponse({
        "result": result,
        "count": count,
        "pages": pages
    })


@shoes_router.post("/add", response_class=JSONResponse)
async def add_shoe(request: Request,
                   file: UploadFile | None = File(None),
                   shoe_name: str = Form(),
                   brand_id: int = Form(),
                   category_ids: str = Form(default=""),
                   demographic_ids: str = Form(default=""),
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
            r'INSERT INTO shoes (shoe_name, brand_id, markup, shoe_price, first_sale_at) VALUES (%s, %s, %s, %s, %s)',
            (shoe_name, brand_id, markup, shoe_price, first_sale_at)
        )

        shoe_id = cursor.lastrowid

        # Add categories
        if category_ids.strip():
            category_list = [int(cat_id.strip())
                             for cat_id in category_ids.split(",") if cat_id.strip()]
            for cat_id in category_list:
                db.commitOne(
                    r'INSERT INTO shoe_categories (shoe_id, category_id) VALUES (%s, %s)',
                    (shoe_id, cat_id)
                )

        # Add demographics
        if demographic_ids.strip():
            demographic_list = [int(demo_id.strip()) for demo_id in demographic_ids.split(
                ",") if demo_id.strip()]
            for demo_id in demographic_list:
                db.commitOne(
                    r'INSERT INTO shoe_demographics (shoe_id, demographic_id) VALUES (%s, %s)',
                    (shoe_id, demo_id)
                )

        # Handle image upload
        if file is not None:
            if not file.content_type or not file.content_type.startswith("image"):
                return JSONResponse(
                    {"success": False,
                        "message": f"Uploaded file ({file.content_type}) is not an image."},
                    status_code=415
                )

            # Create shoe directory
            from ....Settings import Settings
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
            from ....Settings import Settings
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


@shoes_router.post("/update", response_class=JSONResponse)
async def edit_shoe(request: Request,
                    shoe_id: int = Form(),
                    shoe_name: str = Form(),
                    brand_id: int = Form(),
                    category_ids: str = Form(default=""),
                    demographic_ids: str = Form(default=""),
                    markup: int = Form(),
                    shoe_price: float = Form(),
                    first_sale_at: str = Form(),
                    user_perms: list[str] = Depends(user_permissions)):

    utils.check_user_permissions(
        user_perms,
        Permissions.inventory.manage_inventory,
        Permissions.inventory.manage_shoes
    )

    try:

        if brand_id < 0:
            raise DatabaseException("brand_id cannot be negative")

        if shoe_name.strip() == "":
            raise DatabaseException("shoe_name is empty.")

        db.commitOne(
            r'UPDATE shoes SET shoe_name = %s, brand_id = %s, markup = %s, shoe_price = %s, first_sale_at = %s WHERE shoe_id = %s',
            (shoe_name, brand_id, markup, shoe_price, first_sale_at, shoe_id)
        )

        # Delete existing categories and demographics
        db.commitOne(
            r'DELETE FROM shoe_categories WHERE shoe_id = %s', (shoe_id,))
        db.commitOne(
            r'DELETE FROM shoe_demographics WHERE shoe_id = %s', (shoe_id,))

        # Add categories
        if category_ids.strip():
            category_list = [int(cat_id.strip())
                             for cat_id in category_ids.split(",") if cat_id.strip()]
            for cat_id in category_list:
                db.commitOne(
                    r'INSERT INTO shoe_categories (shoe_id, category_id) VALUES (%s, %s)',
                    (shoe_id, cat_id)
                )

        # Add demographics
        if demographic_ids.strip():
            demographic_list = [int(demo_id.strip()) for demo_id in demographic_ids.split(
                ",") if demo_id.strip()]
            for demo_id in demographic_list:
                db.commitOne(
                    r'INSERT INTO shoe_demographics (shoe_id, demographic_id) VALUES (%s, %s)',
                    (shoe_id, demo_id)
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


@shoes_router.delete("/delete/{shoe_id}")
async def delete_shoe(request: Request, shoe_id: int, user_perms: list[str] = Depends(user_permissions)):

    utils.check_user_permissions(
        user_perms,
        Permissions.inventory.manage_inventory,
        Permissions.inventory.manage_shoes
    )

    try:

        db.commitOne(
            r'DELETE FROM shoe_categories WHERE shoe_id = %s', (shoe_id,))
        db.commitOne(
            r'DELETE FROM shoe_demographics WHERE shoe_id = %s', (shoe_id,))

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


@shoes_router.get("/popular", response_class=JSONResponse)
async def list_popular(request: Request, limit: int = 10):

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


@shoes_router.get("/suggestions", response_class=JSONResponse)
async def get_suggestions(request: Request, user_perms: list[str] = Depends(user_permissions)):
    """Get all categories and demographics for autocomplete suggestions"""
    categories = db.fetchAll(r'SELECT * FROM categories')
    demographics = db.fetchAll(r'SELECT * FROM demographics')

    return JSONResponse({
        "categories": categories,
        "demographics": demographics
    })


@shoes_router.get("/{shoe_id}", response_class=JSONResponse)
async def fetch_shoe(request: Request, shoe_id: int, user_perms: list[str] = Depends(user_permissions)):

    return db.fetchOne(r'SELECT * FROM shoes WHERE shoe_id = %s', (shoe_id,))


@shoes_router.get("/{shoe_id}/all", response_class=JSONResponse)
async def fetch_shoe_all_details(request: Request, shoe_id: int, user_perms: list[str] = Depends(user_permissions)):

    if all_shoe_details := db.fetchOne(r"""
                    SELECT *
                    FROM shoes s
                    JOIN brands b ON b.brand_id = s.brand_id
                    WHERE s.shoe_id = %s
                       """,
                                       (shoe_id,)
                                       ):

        all_shoe_details["categories"] = db.fetchAll(
            r"""
            SELECT c.*
            FROM shoe_categories sc
            JOIN categories c ON sc.category_id = c.category_id
            WHERE sc.shoe_id = %s """, (shoe_id,))

        all_shoe_details["demographics"] = db.fetchAll(
            r"""
            SELECT d.*
            FROM shoe_demographics sd
            JOIN demographics d ON sd.demographic_id = d.demographic_id
            WHERE sd.shoe_id = %s """, (shoe_id,))

        return all_shoe_details

    return None


@shoes_router.get("/total/count", response_class=JSONResponse)
async def total_shoes(request: Request, user_perms: list[str] = Depends(user_permissions)):

    result = db.fetchOne(r"SELECT COUNT(*) AS total_count FROM shoes")

    return JSONResponse(result)
