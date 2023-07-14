from fastapi.security import OAuth2 as FastAPIOAuth2
from fastapi.security import OAuth2AuthorizationCodeBearer as FastAPICodeBearer
from fastapi.security import OAuth2PasswordBearer as FastAPIPasswordBearer
from starlette.datastructures import Headers
from starlette.requests import Request


def use_cookie(cls: FastAPIOAuth2):
    def _use_cookie(*args, **kwargs):
        async def __call__(self, request: Request):
            authorization = request.headers.get("Authorization", request.cookies.get("Authorization"))
            if authorization:
                request._headers = Headers({**request.headers, "Authorization": authorization})
            return await super(cls, self).__call__(request)

        cls.__call__ = __call__
        return cls(*args, **kwargs)

    return _use_cookie


@use_cookie
class OAuth2(FastAPIOAuth2):
    ...


@use_cookie
class OAuth2PasswordBearer(FastAPIPasswordBearer):
    ...


@use_cookie
class OAuth2AuthorizationCodeBearer(FastAPICodeBearer):
    ...
