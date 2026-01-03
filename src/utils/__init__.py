import random

import bcrypt
from fastapi import HTTPException

from .permissions import Permissions


def hash_password(password: str):
    salt = bcrypt.gensalt()
    hashed_pw = bcrypt.hashpw(password.encode(), salt)

    return hashed_pw.decode()


def verify_password(password: str, password_hash: str):

    b_password = password.encode()
    b_password_hash = password_hash.encode()

    return bcrypt.checkpw(b_password, b_password_hash)


def check_user_permissions(user_permissions: list[str], *permissions: str):

    for permission in permissions:

        if permission in user_permissions:
            return True

    raise HTTPException(401, "Unauthorized Access - No valid permission")


def generate_otp():

    otp = ""
    for _ in range(6):
        otp += f"{random.randint(0, 9)}"

    return otp
