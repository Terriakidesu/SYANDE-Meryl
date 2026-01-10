import math
import os
import shutil
from io import BytesIO
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, File, Form, Request, UploadFile, Query
from fastapi.responses import JSONResponse
from PIL import Image

from ... import utils
from ...depedencies import is_authenticated, user_permissions
from ...exceptions import DatabaseException
from ...helpers import Database
from ...models.users import UserForm
from ...Settings import Settings
from ...utils import Permissions

users_router = APIRouter(prefix="/users",
                         dependencies=[Depends(is_authenticated)])

db = Database()


@users_router.get("/", response_class=JSONResponse)
async def list_users(request: Request,
                     query: Annotated[Optional[str], Query()] = None,
                     page: Annotated[Optional[int], Query()] = 1,
                     limit: Annotated[Optional[int], Query()] = 10
                     ):

    count = db.fetchOne(r'SELECT COUNT(*) as count FROM users')["count"]
    pages = math.ceil(count / limit)
    offset = (page - 1) * limit

    # Fetch results based on query
    if query:
        results = db.fetchAll(
            r"""
            SELECT u.user_id, u.first_name, u.last_name, u.username, u.created_at, e.email
            FROM users u 
            JOIN emails e ON u.user_id = e.user_id
            WHERE u.user_id = %s OR u.username LIKE %s OR u.first_name LIKE %s OR u.last_name LIKE %s OR e.email = %s
            LIMIT %s OFFSET %s
            """,
            (query, f"%{query}%", f"%{query}%",
             f"%{query}%", query, limit, offset)
        )
    else:
        results = db.fetchAll(
            r"""
            SELECT u.user_id, u.first_name, u.last_name, u.username, u.created_at, e.email
            FROM users u 
            JOIN emails e ON u.user_id = e.user_id
            LIMIT %s OFFSET %s
            """,
            (limit, offset)
        )

    # Enrich users with roles and convert dates to ISO format
    for user in results:
        user["roles"] = db.fetchAll(
            r"""
            SELECT r.* FROM user_roles ur
            JOIN roles r ON ur.role_id = r.role_id
            WHERE ur.user_id = %s
            """, (user["user_id"],))
        if user.get("created_at"):
            user["created_at"] = user["created_at"].isoformat()

    return JSONResponse({
        "result": results,
        "count": count,
        "pages": pages
    })


@users_router.post("/add", response_class=JSONResponse)
async def add_user(request: Request,
                   file: Annotated[UploadFile | None, File()] = None,
                   first_name: str = Form(),
                   last_name: str = Form(),
                   username: str = Form(),
                   password: str = Form(),
                   phone: str = Form(),
                   email: str = Form(),
                   user_perms: list[str] = Depends(user_permissions)
                   ):
    utils.check_user_permissions(
        user_perms,
        Permissions.users.manage_users
    )

    if db.fetchOne(r'SELECT * FROM users WHERE username = %s', (username,)):
        raise DatabaseException("Username is already taken")

    if file is not None:
        if not file.content_type.startswith("image"):  # type: ignore
            return JSONResponse(
                {
                    "success": False,
                    "message": f"Uploaded file ({file.content_type}) is not an image."
                },
                status_code=415
            )

    hashed_pw = utils.hash_password(password)

    cursor = db.commitOne(r'INSERT INTO users (first_name, last_name, username, password) VALUES (%s, %s, %s, %s)',
                          (first_name, last_name, username, hashed_pw))

    db.commitOne(r'INSERT INTO phones (user_id, phone) VALUES (%s, %s)',
                 (cursor.lastrowid, phone))
    db.commitOne(r'INSERT INTO emails (user_id, email) VALUES (%s, %s)',
                 (cursor.lastrowid, email))

    del hashed_pw

    download_path = os.path.join(
        Settings.profiles.path, f"user-{cursor.lastrowid:05d}")
    download_profile_path = os.path.join(
        download_path, f"user-{cursor.lastrowid:05d}.jpeg")

    os.makedirs(download_path, exist_ok=True)

    if file is not None:

        image = Image.open(file.file)

        if image.mode in ('RGBA', 'P'):
            image = image.convert("RGB")

        image = image.resize(
            (Settings.profiles.size, Settings.profiles.size))

        buffer = BytesIO()
        image.save(buffer, format="JPEG", quality=85)
        buffer.seek(0)

        with open(download_profile_path, "wb") as f:
            f.write(buffer.read())

    else:
        shutil.copy(Settings.profiles.default, download_profile_path)

    return {
        "success": True,
        "message": "Successfully added user"
    }


@users_router.post("/update", response_class=JSONResponse)
async def update_user(request: Request, user_id: int = Form(), username: str = Form(), email: str = Form(), first_name: str = Form(default=""), last_name: str = Form(default=""), password: str = Form(default=""), role_ids: list[str] = Form(default=[]), user_perms: list[str] = Depends(user_permissions)):

    if user_id != request.session["user_id"]:
        utils.check_user_permissions(
            user_perms,
            Permissions.users.manage_users
        )

    try:

        if user_id < 0:
            raise DatabaseException("user_id cannot be negative")

        if username.strip() == "":
            raise DatabaseException("username is empty.")

        # Check if username is already taken by another user
        existing = db.fetchOne(r'SELECT user_id FROM users WHERE username = %s AND user_id != %s', (username, user_id))
        if existing:
            raise DatabaseException("Username is already taken")

        db.commitOne(
            r'UPDATE users SET first_name = %s, last_name = %s, username = %s WHERE user_id = %s',
            (first_name, last_name, username, user_id)
        )
        
        # Update email
        db.commitOne(
            r'UPDATE emails SET email = %s WHERE user_id = %s',
            (email, user_id)
        )
        
        # Update password if provided
        if password.strip() != "":
            hashed_pw = utils.hash_password(password)
            db.commitOne(
                r'UPDATE users SET password = %s WHERE user_id = %s',
                (hashed_pw, user_id)
            )
        
        # Update roles
        if role_ids:
            # Convert string IDs to integers
            role_ids = [int(rid) for rid in role_ids]
            
            # Delete existing roles
            db.commitOne(r'DELETE FROM user_roles WHERE user_id = %s', (user_id,))
            
            # Insert new roles
            for role_id in role_ids:
                db.commitOne(
                    r'INSERT INTO user_roles (user_id, role_id) VALUES (%s, %s)',
                    (user_id, role_id)
                )

        return {
            "success": True,
            "message": "Successfully Updated User."
        }
    except Exception as e:
        return JSONResponse({
            "success": False,
            "message": f"{e}"
        },
            status_code=400
        )


@users_router.post("/updatePassword", response_class=JSONResponse)
async def update_user_password(request: Request, user_id: int = Form(), password: str = Form(), user_perms: list[str] = Depends(user_permissions)):

    if user_id != request.session["user_id"]:
        utils.check_user_permissions(
            user_perms,
            Permissions.users.manage_users
        )

    try:

        if user_id < 0:
            raise DatabaseException("user_id cannot be negative")

        if result := db.fetchOne(r'SELECT password FROM users WHERE user_id = %s', (user_id,)):
            password_hash: str = result['password']  # type: ignore

            if utils.verify_password(password, password_hash):
                raise Exception(
                    "New password is the same as the last password.")

        hashed_pw = utils.hash_password(password)

        db.commitOne(
            r'UPDATE users SET password = %s  WHERE user_id = %s',
            (hashed_pw, user_id)
        )

        del hashed_pw

        return {
            "success": True,
            "message": "Successfully Updated User."
        }
    except Exception as e:
        return JSONResponse({
            "success": False,
            "message": f"{e}"
        },
            status_code=400
        )


@users_router.delete("/delete", response_class=JSONResponse)
async def delete_user(request: Request, user_id: int, user_perms: list[str] = Depends(user_permissions)):
    utils.check_user_permissions(
        user_perms,
        Permissions.users.manage_users
    )

    if user_id is None or user_id < 0:
        return JSONResponse(
            {
                "success": False,
                "message": "user_id is invalid."
            }
        )

    try:
        cursor = db.commitOne(
            r'DELETE FROM users WHERE user_id = %s', (user_id,))

        rowCount = cursor.rowcount
        if rowCount <= 0:
            raise DatabaseException("user_id doesn't exist.")

        db.commitOne(r'DELETE FROM phones WHERE user_id = %s', (user_id,))
        db.commitOne(r'DELETE FROM emails WHERE user_id = %s', (user_id,))

        profile_path = os.path.join(
            Settings.profiles.path, f"user-{user_id:05d}")

        shutil.rmtree(profile_path)

        return {
            "success": True,
            "message": "Successfully Deleted User."
        }
    except Exception as e:
        return JSONResponse({
            "success": False,
            "message": f"{e}"
        },
            status_code=400
        )


@users_router.get("/{user_id}", response_class=JSONResponse)
async def fetch_user(request: Request, user_id: Optional[int] = None, user_perms: list[str] = Depends(user_permissions)):
    if user_id is None:
        return JSONResponse({"error": "user_id is required"}, status_code=400)

    user = db.fetchOne(r'SELECT u.user_id, u.username, u.first_name, u.last_name, e.email FROM users u JOIN emails e ON u.user_id = e.user_id WHERE u.user_id = %s', (user_id,))
    
    if not user:
        return JSONResponse({"error": "User not found"}, status_code=404)
    
    # Fetch roles for this user
    roles = db.fetchAll(
        r"""
        SELECT r.role_id, r.role_name FROM user_roles ur
        JOIN roles r ON ur.role_id = r.role_id
        WHERE ur.user_id = %s
        """, (user_id,))
    
    user["roles"] = roles
    return user


@users_router.get("/{user_id}/phones", response_class=JSONResponse)
async def list_user_phone(request: Request, user_id: int, user_perms: list[str] = Depends(user_permissions)):
    utils.check_user_permissions(
        user_perms,
        Permissions.users.manage_users,
        Permissions.users.view_users
    )

    return db.fetchAll(r'SELECT * FROM phones WHERE user_id = %s', (user_id, ))


@users_router.get("/{user_id}/emails", response_class=JSONResponse)
async def list_user_emails(request: Request, user_id: int, user_perms: list[str] = Depends(user_permissions)):
    utils.check_user_permissions(
        user_perms,
        Permissions.users.manage_users,
        Permissions.users.view_users
    )

    return db.fetchAll(r'SELECT * FROM emails WHERE user_id = %s', (user_id, ))


@users_router.get("/{user_id}/roles", response_class=JSONResponse)
async def list_user_roles(request: Request, user_id: int, user_perms: list[str] = Depends(user_permissions)):
    utils.check_user_permissions(
        user_perms,
        Permissions.users.manage_users,
        Permissions.users.view_users
    )

    return db.fetchAll(r'SELECT * FROM user_roles WHERE user_id = %s', (user_id, ))


@users_router.post("/{user_id}/roles/add", response_class=JSONResponse)
async def add_user_role(request: Request, user_id: int, role_id: int = Form(), user_perms: list[str] = Depends(user_permissions)):
    utils.check_user_permissions(
        user_perms,
        Permissions.users.manage_users,
        Permissions.users.view_users
    )

    if not db.fetchOne(r'SELECT * FROM users where user_id = %s', (user_id,)):
        return JSONResponse(
            {
                "success": False,
                "message": "User doesn\'t exist."
            },
            status_code=400
        )

    if db.fetchOne(r'SELECT * FROM roles where role_id = %s', (role_id,)):
        db.commitOne(
            r'INSERT INTO user_roles (user_id, role_id) VALUES (%s, %s)', (user_id, role_id))

        return {
            "success": True,
            "message": "Successfully Added Role to User."
        }

    return JSONResponse(
        {
            "success": False,
            "message": "Role doesn\'t exist."
        },
        status_code=400
    )


@users_router.delete("/{user_id}/roles/delete", response_class=JSONResponse)
async def delete_user_role(request: Request, user_id: int, role_id: int = Form(), user_perms: list[str] = Depends(user_permissions)):
    utils.check_user_permissions(
        user_perms,
        Permissions.users.manage_users
    )

    if not db.fetchOne(r'SELECT * FROM users where user_id = %s', (user_id,)):
        return JSONResponse(
            {
                "success": False,
                "message": "User doesn\'t exist."
            },
            status_code=400
        )

    if db.fetchOne(r'SELECT * FROM roles where role_id = %s', (role_id,)):
        db.commitOne(
            r'DELETE FROM user_roles WHERE user_id = %s AND role_id = %s', (user_id, role_id))

        return {
            "success": True,
            "message": "Successfully Removed Role to User."
        }

    return JSONResponse(
        {
            "success": False,
            "message": "Role doesn\'t exist."
        },
        status_code=400
    )


@users_router.get("/{user_id}/roles/{role_id}", response_class=JSONResponse)
async def fetch_user_role(request: Request, user_id: int, role_id, user_perms: list[str] = Depends(user_permissions)):
    utils.check_user_permissions(
        user_perms,
        Permissions.users.manage_users,
        Permissions.users.view_users
    )

    return db.fetchOne(
        r'SELECT * FROM user_roles WHERE user_id = %s AND role_id = %s', (user_id, role_id))


@users_router.get("/{user_id}/roles/{role_id}/permissions", response_class=JSONResponse)
async def list_user_role_permissions(request: Request, user_id: int, role_id: int, user_perms: list[str] = Depends(user_permissions)):
    utils.check_user_permissions(
        user_perms,
        Permissions.users.manage_users,
        Permissions.users.view_users
    )

    return db.fetchAll(r"""
                    SELECT p.*
                    FROM user_roles ur
                    JOIN role_permissions rp ON rp.role_id = ur.role_id
                    JOIN permissions p ON rp.permission_id = p.permission_id
                    WHERE ur.user_id = %s AND rp.role_id = %s
                    """, (user_id, role_id))


@users_router.get("/{user_id}/roles/{role_id}/permissions/{permission_id}", response_class=JSONResponse)
async def fetch_user_role_permission(request: Request, user_id: int, role_id: int, permission_id: int, user_perms: list[str] = Depends(user_permissions)):
    utils.check_user_permissions(
        user_perms,
        Permissions.users.manage_users,
        Permissions.users.view_users
    )

    return db.fetchOne(r"""
                    SELECT p.*
                    FROM user_roles ur
                    JOIN role_permissions rp ON rp.role_id = ur.role_id
                    JOIN permissions p ON rp.permission_id = p.permission_id
                    WHERE ur.user_id = %s AND rp.role_id = %s AND rp.permission_id = %s
                    """, (user_id, role_id, permission_id))
