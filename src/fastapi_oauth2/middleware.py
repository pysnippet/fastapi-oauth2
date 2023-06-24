from typing import Optional, Tuple, Union

from fastapi.security.utils import get_authorization_scheme_param
from starlette.authentication import AuthenticationBackend, AuthCredentials
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.requests import Request
from starlette.types import Send, Receive, Scope, ASGIApp

from .types import Config
from .types import ConfigParams
from .utils import jwt_decode


class OAuth2Backend(AuthenticationBackend):
    async def authenticate(self, request: Request) -> Optional[Tuple["AuthCredentials", Optional[dict]]]:
        authorization = request.cookies.get("Authorization")
        scheme, param = get_authorization_scheme_param(authorization)

        if not scheme or not param:
            return AuthCredentials(), None

        access_token = jwt_decode(param)
        scope = access_token.pop("scope")
        return AuthCredentials(scope), access_token


class OAuth2Middleware:
    def __init__(self, app: ASGIApp, config: Union[Config, ConfigParams]) -> None:
        if isinstance(config, Config):
            self.config = config
        elif isinstance(config, dict):
            self.config = Config(**config)
        else:
            raise ValueError("config does not contain valid parameters")
        self.auth_middleware = AuthenticationMiddleware(app, OAuth2Backend())

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        await self.auth_middleware(scope, receive, send)
