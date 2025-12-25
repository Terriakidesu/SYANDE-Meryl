import os
import shutil
from io import BytesIO
from typing import Annotated, Optional

import bcrypt
from fastapi import APIRouter, File, Form, Request, UploadFile
from fastapi.responses import JSONResponse
from PIL import Image

from ... import utils
from ...exceptions import DatabaseException
from ...includes import Database
from ...models.users import UserForm
from ...Settings import Settings

users_router = APIRouter(prefix="/api/users")

db = Database()


@users_router.get("/", response_class=JSONResponse)
async def list_users(request: Request):
    return db.fetchAll(r'SELECT * FROM users')


@users_router.post("/add", response_class=JSONResponse)
async def add_user(request: Request,
                   file: Annotated[UploadFile | None, File()] = None,
                   first_name: str = Form(),
                   last_name: str = Form(),
                   username: str = Form(),
                   password: str = Form(),
                   phone: str = Form(),
                   email: str = Form()
                   ):

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
async def update_user(request: Request, user: Annotated[UserForm, Form()]):
    try:

        if user.user_id < 0:
            raise DatabaseException("user_id cannot be negative")

        if user.username.strip() == "":
            raise DatabaseException("username is empty.")

        if user.first_name.strip() == "":
            raise DatabaseException("first_name is empty.")

        if user.last_name.strip() == "":
            raise DatabaseException("last_name is empty.")

        if db.fetchOne(r'SELECT * FROM users WHERE username = %s', (user.username)):
            raise DatabaseException("Username is already taken")

        db.commitOne(
            r'UPDATE users SET first_name = %s, last_name = %s, username = %s  WHERE user_id = %s',
            (user.first_name, user.last_name, user.username, user.user_id)
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
async def update_user_password(request: Request, user_id: int = Form(), password: str = Form()):
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
async def delete_user(request: Request, user_id: int):

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
async def fetch_user(request: Request, user_id: Optional[int] = None):

    if user_id is None:
        return []

    return db.fetchAll(r'SELECT * FROM users WHERE user_id = %s', (user_id,))


@users_router.get("/{user_id}/phones", response_class=JSONResponse)
async def list_user_phone(request: Request, user_id: int):

    return db.fetchAll(r'SELECT * FROM phones WHERE user_id = %s', (user_id, ))


@users_router.get("/{user_id}/emails", response_class=JSONResponse)
async def list_user_emails(request: Request, user_id: int):

    return db.fetchAll(r'SELECT * FROM emails WHERE user_id = %s', (user_id, ))


@users_router.get("/{user_id}/roles", response_class=JSONResponse)
async def list_user_roles(request: Request, user_id: int):

    return db.fetchAll(r'SELECT * FROM user_roles WHERE user_id = %s', (user_id, ))


@users_router.post("/{user_id}/roles/add", response_class=JSONResponse)
async def add_user_role(request: Request, user_id: int, role_id: int = Form()):

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
async def delete_user_role(request: Request, user_id: int, role_id: int = Form()):

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
async def fetch_user_role(request: Request, user_id: int, role_id):

    return db.fetchOne(
        r'SELECT * FROM user_roles WHERE user_id = %s AND role_id = %s', (user_id, role_id))


@users_router.get("/{user_id}/roles/{role_id}/permissions", response_class=JSONResponse)
async def list_user_role_permissions(request: Request, user_id: int, role_id: int):

    role = db.fetchOne(
        r'SELECT * FROM user_roles WHERE user_id = %s AND role_id = %s', (user_id, role_id))

    if role is None:
        return []

    return db.fetchAll(r'SELECT * FROM role_permissions WHERE role_id', (role_id,))


@users_router.get("/{user_id}/roles/{role_id}/permissions/{permission_id}", response_class=JSONResponse)
async def fetch_user_role_permission(request: Request, user_id: int, role_id: int, permission_id: int):

    role = db.fetchOne(
        r'SELECT * FROM user_roles WHERE user_id = %s AND role_id = %s', (user_id, role_id))

    if role is None:
        return []

    return db.fetchAll(r'SELECT * FROM role_permissions WHERE role_id = %s AND permission_id = %s', (role_id, permission_id))
