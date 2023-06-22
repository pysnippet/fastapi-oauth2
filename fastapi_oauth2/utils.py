from datetime import datetime, timedelta
from typing import Optional

from jose import jwt

from .config import JWT_SECRET, JWT_ALGORITHM


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    expire = datetime.utcnow() + expires_delta if expires_delta else timedelta(minutes=15)
    return jwt.encode({**data, "exp": expire}, JWT_SECRET, algorithm=JWT_ALGORITHM)
