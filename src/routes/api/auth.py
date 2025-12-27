from datetime import datetime

from fastapi import APIRouter, Request, Form
from fastapi.responses import JSONResponse, RedirectResponse

from ...includes import Database
from ...exceptions import DatabaseException
from ...models.users import User
from ...models.session import Session
from ... import utils

auth_router = APIRouter(prefix="/api/auth")

db = Database()


@auth_router.post("/register", response_class=JSONResponse)
async def register(request: Request,
                   first_name: str = Form(),
                   last_name: str = Form(),
                   username: str = Form(),
                   password: str = Form(),
                   phone: str = Form(),
                   email: str = Form()):

    try:
        if db.fetchOne(r'SELECT * FROM users WHERE username = %s', (username,)):
            raise DatabaseException("Username is already taken")

        hashed_pw = utils.hash_password(password)

        cursor = db.commitOne(r'INSERT INTO users (first_name, last_name, username, password) VALUES (%s, %s, %s, %s)',
                              (first_name, last_name, username, hashed_pw))

        db.commitOne(r'INSERT INTO phones (user_id, phone) VALUES (%s, %s)',
                     (cursor.lastrowid, phone))
        db.commitOne(r'INSERT INTO emails (user_id, email) VALUES (%s, %s)',
                     (cursor.lastrowid, email))

        del hashed_pw

        # Note: Profile handling omitted for simplicity

        return JSONResponse({
            "success": True,
            "message": "User registered successfully"
        }, status_code=201)
    except Exception as e:
        return JSONResponse({
            "success": False,
            "message": f"{e}"
        },
            status_code=400
        )


@auth_router.post("/login", response_class=JSONResponse)
async def login(request: Request, username: str = Form(), password: str = Form()):

    if request.session.get("authenticated"):
        return JSONResponse({
            "success": False,
            "message": f"An user is already logged in."
        },
            status_code=406
        )

    try:
        user = db.fetchOne(
            r'SELECT user_id, first_name, last_name, username, password FROM users WHERE username = %s', (username,))
        if not user:
            raise DatabaseException("Incorrect username or password")

        if not utils.verify_password(password, user['password']):
            raise DatabaseException("Incorrect username or password")

        user = User(**user)

        request.session["authenticated"] = True
        request.session["user_id"] = user.user_id
        request.session["username"] = user.username
        request.session["logged_at"] = datetime.now().timestamp()

        return {
            "success": True,
            "message": "User logged in successfully."
        }
    except Exception as e:
        return JSONResponse({
            "success": False,
            "message": f"{e}"
        },
            status_code=400
        )


@auth_router.post("/logout")
async def logout(request: Request):

    if not request.session.get("authenticated"):
        return JSONResponse({
            "success": False,
            "message": f"Login first."
        },
            status_code=406
        )

    try:

        request.session.clear()

        return {
            "success": True,
            "message": "User logged out successfully."
        }

    except Exception as e:

        return JSONResponse({
            "success": False,
            "message": f"{e}"
        },
            status_code=400
        )
