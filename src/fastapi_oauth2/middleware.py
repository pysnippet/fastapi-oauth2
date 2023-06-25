from typing import List
from typing import Optional
from typing import Tuple
from typing import Union

from fastapi.security.utils import get_authorization_scheme_param
from starlette.authentication import AuthenticationBackend
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.requests import Request
from starlette.types import ASGIApp
from starlette.types import Receive
from starlette.types import Scope
from starlette.types import Send

from .config import OAuth2Config
from .utils import jwt_decode


class Auth:
    scopes: List[str]

    def __init__(self, scopes: Optional[List[str]] = None) -> None:
        self.scopes = scopes or []


class User(dict):
    is_authenticated: bool

    def __init__(self, seq: Optional[dict] = None, **kwargs) -> None:
        self.is_authenticated = seq is not None
        super().__init__(seq or {}, **kwargs)


class OAuth2Backend(AuthenticationBackend):
    async def authenticate(self, request: Request) -> Optional[Tuple["Auth", "User"]]:
        authorization = request.cookies.get("Authorization")
        scheme, param = get_authorization_scheme_param(authorization)

        if not scheme or not param:
            return Auth(), User()

        user = jwt_decode(param)
        scopes = user.pop("scope")
        return Auth(scopes), User(user)


class OAuth2Middleware:
    config: OAuth2Config
    auth_middleware: AuthenticationMiddleware

    def __init__(self, app: ASGIApp, config: Union[OAuth2Config, dict]) -> None:
        if isinstance(config, OAuth2Config):
            self.config = config
        elif isinstance(config, dict):
            self.config = OAuth2Config(**config)
        else:
            raise TypeError("config is not a valid type")
        self.auth_middleware = AuthenticationMiddleware(app, OAuth2Backend())

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        await self.auth_middleware(scope, receive, send)
