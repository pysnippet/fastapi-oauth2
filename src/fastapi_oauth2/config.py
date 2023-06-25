import os
from typing import List

from dotenv import load_dotenv

from .client import OAuth2Client

load_dotenv()

OAUTH2_CLIENT_ID = os.getenv("OAUTH2_CLIENT_ID")
OAUTH2_CLIENT_SECRET = os.getenv("OAUTH2_CLIENT_SECRET")
OAUTH2_CALLBACK_URL = os.getenv("OAUTH2_CALLBACK_URL")

JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")
JWT_EXPIRES = int(os.getenv("JWT_EXPIRES", "15"))


class OAuth2Config:
    allow_http: bool
    jwt_secret: str
    jwt_expires: int
    jwt_algorithm: str
    clients: List[OAuth2Client]

    def __init__(
            self,
            *,
            allow_http: bool = False,
            jwt_secret: str = "",
            jwt_expires: int = 900,
            jwt_algorithm: str = "HS256",
            clients: List[OAuth2Client] = None,
    ):
        self.allow_http = allow_http
        self.jwt_secret = jwt_secret
        self.jwt_expires = jwt_expires
        self.jwt_algorithm = jwt_algorithm
        self.clients = clients or []
