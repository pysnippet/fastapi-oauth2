import pytest

from fastapi_oauth2.security import OAuth2
from fastapi_oauth2.security import OAuth2AuthorizationCodeBearer
from fastapi_oauth2.security import OAuth2PasswordBearer


@pytest.mark.anyio
async def test_security_oauth2(get_app):
    try:
        get_app(OAuth2())
    except (TypeError, Exception):
        assert False


@pytest.mark.anyio
async def test_security_oauth2_password_bearer(get_app):
    try:
        get_app(OAuth2PasswordBearer(tokenUrl="/test"))
    except (TypeError, Exception):
        assert False


@pytest.mark.anyio
async def test_security_oauth2_authentication_code_bearer(get_app):
    try:
        get_app(OAuth2AuthorizationCodeBearer(authorizationUrl="/test", tokenUrl="/test"))
    except (TypeError, Exception):
        assert False
