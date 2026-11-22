import time
import warnings

import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from jose import jwt

from fastapi_oauth2.config import OAuth2Config
from fastapi_oauth2.middleware import OAuth2Middleware
from tests.conftest import TEST_JWT_SECRET


@pytest.mark.parametrize("kwargs", [
    {},
    {"jwt_secret": None},
    {"jwt_secret": ""},
    {"jwt_secret": "   "},
    {"jwt_secret": b""},
    {"jwt_secret": b"   "},
])
def test_config_requires_jwt_secret(kwargs):
    with pytest.raises(ValueError):
        OAuth2Config(**kwargs)


def test_middleware_dict_config_requires_jwt_secret():
    with pytest.raises(ValueError):
        OAuth2Middleware(FastAPI(), config={"allow_http": True})


def test_config_warns_on_short_hmac_secret():
    with pytest.warns(UserWarning):
        OAuth2Config(jwt_secret="secret")


def test_config_accepts_strong_secret():
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        config = OAuth2Config(jwt_secret=TEST_JWT_SECRET)
    assert config.jwt_secret == TEST_JWT_SECRET


def test_config_warns_on_short_bytes_secret():
    with pytest.warns(UserWarning):
        OAuth2Config(jwt_secret=b"short")


def test_config_unset_env_values_fall_back_to_defaults():
    # e.g. jwt_algorithm=os.getenv("JWT_ALGORITHM") when the variable is not set
    config = OAuth2Config(jwt_secret=TEST_JWT_SECRET, jwt_algorithm=None, jwt_expires=None)
    assert config.jwt_algorithm == "HS256"
    assert config.jwt_expires == 900


@pytest.mark.anyio
async def test_middleware_rejects_empty_key_forgery(get_app):
    # GHSA-vqgm-5gxf-445v: a token signed with the empty HMAC key must not authenticate
    forged = jwt.encode({
        "sub": "admin",
        "provider": "github",
        "scope": ["admin"],
        "exp": int(time.time()) + 3600,
    }, "", algorithm="HS256")

    async with AsyncClient(app=get_app(with_ssr=False), base_url="http://test") as client:
        response = await client.get("/user", headers={"Authorization": "Bearer %s" % forged})
        assert response.status_code == 400

        client.cookies.update(dict(Authorization="Bearer %s" % forged))
        response = await client.get("/user")
        assert response.status_code == 400


@pytest.mark.anyio
async def test_middleware_rejects_token_without_exp(get_app):
    token = jwt.encode({"sub": "1234567890", "provider": "github"}, TEST_JWT_SECRET, algorithm="HS256")
    async with AsyncClient(app=get_app(with_ssr=False), base_url="http://test") as client:
        response = await client.get("/user", headers={"Authorization": "Bearer %s" % token})
        assert response.status_code == 400
