from typing import Annotated, Optional
from datetime import datetime

from fastapi import APIRouter, Request, Form
from fastapi.responses import JSONResponse, RedirectResponse

from ...includes import Database
from ...exceptions import DatabaseException
from ...models.users import User
from ...models.session import Session
from ...helpers.email.OTP_mail import send_otp_email
from ... import utils

auth_router = APIRouter(prefix="/auth")

db = Database()


@auth_router.post("/register", response_class=JSONResponse)
async def register(request: Request,
                   first_name: str = Form(),
                   last_name: str = Form(),
                   username: str = Form(),
                   password: str = Form(),
                   email: str = Form()):

    if not request.session.get("otp_verified"):
        return JSONResponse({
            "success": False,
            "message": "Unathorized Registration."
        },
            status_code=400
        )

    try:
        if db.fetchOne(r'SELECT * FROM users WHERE username = %s', (username,)):
            raise DatabaseException("Username is already taken")

        hashed_pw = utils.hash_password(password)

        cursor = db.commitOne(r'INSERT INTO users (first_name, last_name, username, password) VALUES (%s, %s, %s, %s)',
                              (first_name, last_name, username, hashed_pw))

        db.commitOne(r'INSERT INTO emails (user_id, email) VALUES (%s, %s)',
                     (cursor.lastrowid, email))

        del hashed_pw

        # Note: Profile handling omitted for simplicity

        request.session.pop("otp_verified", None)

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
async def login(request: Request, email: str = Form(), password: str = Form()):

    if request.session.get("authenticated"):
        return JSONResponse({
            "success": False,
            "message": f"A user is already logged in."
        },
            status_code=406
        )

    # NOTE: TEMPORARY
    # TODO: Will change to a more secure one
    if email == "superadmin":
        request.session["authenticated"] = True
        request.session["superadmin"] = True
        request.session["username"] = "superadmin"
        request.session["logged_at"] = datetime.now().timestamp()
        return {
            "success": True,
            "message": "User logged in successfully."
        }

    try:
        user = db.fetchOne(
            r"""
            SELECT *
            FROM emails e
            JOIN users u ON u.user_id = e.user_id
            WHERE email = %s OR username = %s
            """,
            (email, email)
        )
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


@auth_router.post("/request_otp")
async def request_otp(request: Request, email: str = Form(), request_new: Annotated[bool, Form()] = False):

    if request.session.get("authenticated"):
        return JSONResponse({
            "success": False,
            "message": "User is logged in"
        },
            status_code=406
        )

    if email is None:
        return JSONResponse({
            "success": False,
            "message": "Email is invalid or empty."
        },
            status_code=406
        )

    # Check if OTP is still valid (not expired)
    if request.session.get("otp") and not request_new:

        otp_timestamp = request.session.get("otp_timestamp")
        if otp_timestamp:
            otp_timestamp = datetime.fromtimestamp(otp_timestamp)
            otp_timeout = 10 * 60  # 10 minutes
            otp_elapsed_time = datetime.now() - otp_timestamp

            if otp_elapsed_time.total_seconds() < otp_timeout:
                return JSONResponse({
                    "success": False,
                    "message": "OTP is still valid. Please wait for it to expire or verify the current OTP."
                },
                    status_code=406
                )

    # Check OTP cooldown (30 seconds between requests)
    if request.session.get("otp_cooldown_timestamp"):
        otp_cooldown = request.session.get("otp_cooldown_timestamp")
        otp_cooldown = datetime.fromtimestamp(otp_cooldown)
        otp_cooldown_elapsed = datetime.now() - otp_cooldown

        if otp_cooldown_elapsed.total_seconds() < 30:
            remaining_cooldown = 30 - otp_cooldown_elapsed.total_seconds()
            return JSONResponse({
                "success": False,
                "message": f"OTP request is on cooldown. Please wait {int(remaining_cooldown)} seconds."
            },
                status_code=406
            )

    try:
        otp = utils.generate_otp()

        send_otp_email(email, otp)

        request.session["otp"] = otp
        request.session["email"] = email
        request.session["otp_timestamp"] = datetime.now().timestamp()
        request.session["otp_cooldown_timestamp"] = datetime.now().timestamp()

        return JSONResponse({
            "success": True,
            "message": "OTP Sent"
        },
            status_code=200
        )

    except Exception as e:
        return JSONResponse({
            "success": False,
            "message": f"{type(e)}: {e}"
        },
            status_code=406
        )


@auth_router.post("/verify_otp")
async def verify_otp(request: Request, otp: str = Form()):

    if request.session.get("authenticated"):
        return JSONResponse({
            "success": False,
            "message": "User is logged in"
        },
            status_code=406
        )

    if otp is None:
        return JSONResponse({
            "success": False,
            "message": "OTP is empty."
        },
            status_code=406
        )

    # Check if OTP exists in session
    server_otp = request.session.get("otp")
    if not server_otp:
        return JSONResponse({
            "success": False,
            "message": "No OTP found. Please request a new OTP."
        },
            status_code=406
        )

    # Check if OTP timestamp exists and validate expiration
    if otp_timestamp := request.session.get("otp_timestamp"):
        otp_timestamp = datetime.fromtimestamp(otp_timestamp)
        otp_timeout = 10 * 60  # 10 minutes

        otp_elapsed_time = datetime.now() - otp_timestamp

        if otp_elapsed_time.total_seconds() >= otp_timeout:
            # Clean up expired OTP
            request.session.pop("otp", None)
            request.session.pop("otp_cooldown_timestamp", None)
            request.session.pop("otp_timestamp", None)

            return JSONResponse({
                "success": False,
                "message": "OTP Expired. Please request a new OTP."
            },
                status_code=406
            )

    # Validate OTP
    if otp == server_otp:
        request.session["otp_verified"] = True

        # Clean up session data after successful verification
        request.session.pop("otp", None)
        request.session.pop("otp_cooldown_timestamp", None)
        request.session.pop("otp_timestamp", None)

        # Get email from session for potential user creation or login
        email = request.session.pop("email", None)

        return JSONResponse({
            "success": True,
            "message": "OTP matches",
            "email": email
        },
            status_code=200
        )

    return JSONResponse({
        "success": False,
        "message": "OTP is invalid."
    },
        status_code=200
    )


@auth_router.post("/verify_email")
async def verify_email(request: Request, email: str = Form()):
    if request.session.get("authenticated"):
        return JSONResponse({
            "success": False,
            "message": "User is logged in"
        },
            status_code=406
        )

    if email is None:
        return JSONResponse({
            "success": False,
            "message": "email is empty."
        },
            status_code=406
        )

    if _ := db.fetchOne(r"SELECT * FROM emails where email = %s", (email,)):
        return JSONResponse({
            "success": False,
            "message": "email is already in use."
        },
            status_code=406
        )

    return JSONResponse({
        "success": True,
        "message": "email is not in use."
    },
        status_code=200
    )
