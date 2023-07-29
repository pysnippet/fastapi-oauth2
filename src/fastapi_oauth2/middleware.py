from datetime import datetime
from datetime import timedelta
from typing import Any
from typing import Awaitable
from typing import Callable
from typing import Dict
from typing import List
from typing import Optional
from typing import Sequence
from typing import Tuple
from typing import Union

from fastapi.security.utils import get_authorization_scheme_param
from jose.jwt import decode as jwt_decode
from jose.jwt import encode as jwt_encode
from starlette.authentication import AuthCredentials
from starlette.authentication import AuthenticationBackend
from starlette.authentication import BaseUser
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.requests import Request
from starlette.types import ASGIApp
from starlette.types import Receive
from starlette.types import Scope
from starlette.types import Send

from .claims import Claims
from .client import OAuth2Client
from .config import OAuth2Config
from .core import OAuth2Core


class Auth(AuthCredentials):
    """Extended auth credentials schema based on Starlette AuthCredentials."""

    http: bool
    secret: str
    expires: int
    algorithm: str
    scopes: List[str]
    clients: Dict[str, OAuth2Core] = {}

    provider: str
    default_provider: str = "local"

    def __init__(
            self,
            scopes: Optional[Sequence[str]] = None,
            provider: str = default_provider,
    ) -> None:
        super().__init__(scopes)
        self.provider = provider

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


class User(BaseUser, dict):
    """Extended user schema based on Starlette BaseUser."""

    @property
    def is_authenticated(self) -> bool:
        return bool(self)

    @property
    def display_name(self) -> str:
        return self.__getprop__("display_name")

    @property
    def identity(self) -> str:
        return self.__getprop__("identity")

    @property
    def picture(self) -> str:
        return self.__getprop__("picture")

    @property
    def email(self) -> str:
        return self.__getprop__("email")

    def use_claims(self, claims: Claims) -> "User":
        for attr, item in claims.items():
            self[attr] = self.__getprop__(item)
        return self

    def __getprop__(self, item, default="") -> Any:
        if callable(item):
            return item(self)
        return self.get(item, default)


class OAuth2Backend(AuthenticationBackend):
    """Authentication backend for AuthenticationMiddleware."""

    def __init__(
            self,
            config: OAuth2Config,
            callback: Callable[[Auth, User], Union[Awaitable[None], None]] = None,
    ) -> None:
        Auth.set_http(config.allow_http)
        Auth.set_secret(config.jwt_secret)
        Auth.set_expires(config.jwt_expires)
        Auth.set_algorithm(config.jwt_algorithm)
        for client in config.clients:
            Auth.register_client(client)
        self.callback = callback

    async def authenticate(self, request: Request) -> Optional[Tuple[Auth, User]]:
        authorization = request.headers.get(
            "Authorization",
            request.cookies.get("Authorization"),
        )
        scheme, param = get_authorization_scheme_param(authorization)

        if not scheme or not param:
            return Auth(), User()

        user = User(Auth.jwt_decode(param))
        user.update(provider=user.get("provider", Auth.default_provider))
        auth = Auth(user.pop("scope", []), user.get("provider"))
        client = Auth.clients.get(auth.provider)
        claims = client.claims if client else Claims()
        user = user.use_claims(claims)

        # Call the callback function on authentication
        if callable(self.callback):
            coroutine = self.callback(auth, user)
            if issubclass(type(coroutine), Awaitable):
                await coroutine
        return auth, user


class OAuth2Middleware:
    """Wrapper for the Starlette AuthenticationMiddleware."""

    auth_middleware: AuthenticationMiddleware = None

    def __init__(
            self,
            app: ASGIApp,
            config: Union[OAuth2Config, dict],
            callback: Callable[[Auth, User], Union[Awaitable[None], None]] = None,
            **kwargs,  # AuthenticationMiddleware kwargs
    ) -> None:
        """Initiates the middleware with the given configuration.

        :param app: FastAPI application instance
        :param config: middleware configuration
        :param callback: callback function to be called after authentication
        """
        if isinstance(config, dict):
            config = OAuth2Config(**config)
        elif not isinstance(config, OAuth2Config):
            raise TypeError("config is not a valid type")
        self.auth_middleware = AuthenticationMiddleware(app, backend=OAuth2Backend(config, callback), **kwargs)

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        await self.auth_middleware(scope, receive, send)
