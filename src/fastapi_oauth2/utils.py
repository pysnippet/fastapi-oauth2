from datetime import datetime, timedelta

from jose import jwt

from .config import JWT_SECRET, JWT_ALGORITHM, JWT_EXPIRES


def jwt_encode(data: dict) -> str:
    return jwt.encode(data, JWT_SECRET, algorithm=JWT_ALGORITHM)


def jwt_decode(token: str) -> dict:
    return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])


def jwt_create(token_data: dict) -> str:
    expire = datetime.utcnow() + timedelta(minutes=JWT_EXPIRES)
    return jwt_encode({**token_data, "exp": expire})
