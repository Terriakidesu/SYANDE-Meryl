import math
import os
import shutil
from io import BytesIO
from typing import Annotated, Optional

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
                     page: Annotated[Optional[int], Query()] = 1,
                     limit: Annotated[Optional[int], Query()] = 10
                     ):

    count = db.fetchOne(r'SELECT COUNT(*) as count FROM shoes')["count"]
    pages = math.ceil(count / limit)
    offset = (page - 1) * limit

    if query:
        result = db.fetchAll(
            r"""
            SELECT * 
            FROM shoes 
            WHERE shoe_id = %s OR shoe_name LIKE %s 
            LIMIT %s OFFSET %s""",
            (query, f"%{query}%", limit, offset)
        )

    else:
        result = db.fetchAll(
            r"""
            SELECT * 
            FROM shoes 
            LIMIT %s OFFSET %s""",
            (limit, offset)
        )

    for shoe in result:
        shoe_id = shoe["shoe_id"]
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
                   category_id: int = Form(),
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
            r'INSERT INTO shoes (shoe_name, brand_id, markup, shoe_price, first_sale_at) VALUES (%s, %s, %s, %s, %s, %s)',
            (shoe_name, brand_id, category_id,
             markup, shoe_price, first_sale_at)
        )

        shoe_id = cursor.lastrowid

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
async def edit_shoe(request: Request, shoe: Annotated[Shoe, Form()], user_perms: list[str] = Depends(user_permissions)):

    utils.check_user_permissions(
        user_perms,
        Permissions.inventory.manage_inventory,
        Permissions.inventory.manage_shoes
    )

    try:

        if shoe.brand_id < 0:
            raise DatabaseException("brand_id cannot be negative")

        if shoe.shoe_name.strip() == "":
            raise DatabaseException("brand_name is empty.")

        db.commitOne(
            r'UPDATE shoes SET shoe_name = %s, brand_id = %s, category_id = %s, markup = %s, shoe_price = %s, first_sale_at = %s  WHERE shoe_id = %s',
            (shoe.shoe_name, shoe.brand_id, shoe.category_id, shoe.markup,
             shoe.shoe_price, shoe.first_sale_at, shoe.shoe_id)
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
async def list_popular(request: Request, limit: int = 10, user_perms: list[str] = Depends(user_permissions)):

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
            r'SELECT * FROM categories WHERE shoe_id = %s', (shoe_id,))

        return all_shoe_details

    return None
