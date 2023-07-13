from datetime import datetime
from datetime import timedelta
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union

from fastapi.security.utils import get_authorization_scheme_param
from jose.jwt import decode as jwt_decode
from jose.jwt import encode as jwt_encode
from starlette.authentication import AuthenticationBackend
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.requests import Request
from starlette.types import ASGIApp
from starlette.types import Receive
from starlette.types import Scope
from starlette.types import Send

from .client import OAuth2Client
from .config import OAuth2Config
from .core import OAuth2Core


class Auth:
    http: bool
    secret: str
    expires: int
    algorithm: str
    scopes: List[str]
    clients: Dict[str, OAuth2Core] = {}

    def __init__(self, scopes: Optional[List[str]] = None) -> None:
        self.scopes = scopes or []

    @classmethod
    def set_http(cls, http: bool) -> None:
        cls.http = http

    @classmethod
    def set_secret(cls, secret: str) -> None:
        cls.secret = secret

    @classmethod
    def set_expires(cls, expires: int) -> None:
        cls.expires = expires

    @classmethod
    def set_algorithm(cls, algorithm: str) -> None:
        cls.algorithm = algorithm

    @classmethod
    def register_client(cls, client: OAuth2Client) -> None:
        cls.clients[client.backend.name] = OAuth2Core(client)

    @classmethod
    def jwt_encode(cls, data: dict) -> str:
        return jwt_encode(data, cls.secret, algorithm=cls.algorithm)

    @classmethod
    def jwt_decode(cls, token: str) -> dict:
        return jwt_decode(token, cls.secret, algorithms=[cls.algorithm])

    @classmethod
    def jwt_create(cls, token_data: dict) -> str:
        expire = datetime.utcnow() + timedelta(seconds=cls.expires)
        return cls.jwt_encode({**token_data, "exp": expire})


class User(dict):
    is_authenticated: bool

    def __init__(self, seq: Optional[dict] = None, **kwargs) -> None:
        self.is_authenticated = seq is not None
        super().__init__(seq or {}, **kwargs)


class OAuth2Backend(AuthenticationBackend):
    def __init__(self, config: OAuth2Config) -> None:
        Auth.set_http(config.allow_http)
        Auth.set_secret(config.jwt_secret)
        Auth.set_expires(config.jwt_expires)
        Auth.set_algorithm(config.jwt_algorithm)
        for client in config.clients:
            Auth.register_client(client)

    async def authenticate(self, request: Request) -> Optional[Tuple["Auth", "User"]]:
        authorization = request.headers.get(
            "Authorization",
            request.cookies.get("Authorization"),
        )
        scheme, param = get_authorization_scheme_param(authorization)

        if not scheme or not param:
            return Auth(), User()

        user = Auth.jwt_decode(param)
        return Auth(user.pop("scope")), User(user)


class OAuth2Middleware:
    auth_middleware: AuthenticationMiddleware = None

    def __init__(self, app: ASGIApp, config: Union[OAuth2Config, dict]) -> None:
        if isinstance(config, dict):
            config = OAuth2Config(**config)
        elif not isinstance(config, OAuth2Config):
            raise TypeError("config is not a valid type")
        self.auth_middleware = AuthenticationMiddleware(app, OAuth2Backend(config))

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        await self.auth_middleware(scope, receive, send)
