from typing import Any
from typing import Callable
from typing import Dict
from typing import Optional
from typing import Tuple
from typing import Type

from fastapi.security import OAuth2 as FastAPIOAuth2
from fastapi.security import OAuth2AuthorizationCodeBearer as FastAPICodeBearer
from fastapi.security import OAuth2PasswordBearer as FastAPIPasswordBearer
from starlette.datastructures import Headers
from starlette.requests import Request


def use_cookies(cls: Type[FastAPIOAuth2]) -> Callable[[Tuple[Any], Dict[str, Any]], FastAPIOAuth2]:
    """OAuth2 classes wrapped with this decorator will use cookies for the Authorization header."""

    def _use_cookies(*args, **kwargs) -> FastAPIOAuth2:
        async def __call__(self: FastAPIOAuth2, request: Request) -> Optional[str]:
            authorization = request.headers.get("Authorization", request.cookies.get("Authorization"))
            if authorization:
                request._headers = Headers({**request.headers, "Authorization": authorization})
            return await super(cls, self).__call__(request)

        cls.__call__ = __call__
        return cls(*args, **kwargs)

    return _use_cookies


@use_cookies
class OAuth2(FastAPIOAuth2):
    """Wrapper class of the `fastapi.security.OAuth2` class."""


@use_cookies
class OAuth2PasswordBearer(FastAPIPasswordBearer):
    """Wrapper class of the `fastapi.security.OAuth2PasswordBearer` class."""


@use_cookies
class OAuth2AuthorizationCodeBearer(FastAPICodeBearer):
    """Wrapper class of the `fastapi.security.OAuth2AuthorizationCodeBearer` class."""
