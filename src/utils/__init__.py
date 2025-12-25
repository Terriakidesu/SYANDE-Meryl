import bcrypt


def hash_password(password: str):
    salt = bcrypt.gensalt()
    hashed_pw = bcrypt.hashpw(password.encode(), salt)

    return hashed_pw.decode()


def verify_password(password: str, password_hash: str):

    b_password = password.encode()
    b_password_hash = password_hash.encode()

    return bcrypt.checkpw(b_password, b_password_hash)
