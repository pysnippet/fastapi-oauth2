import importlib
import os

import pytest
import social_core.backends as backends
from fastapi import APIRouter
from fastapi import FastAPI
from httpx import AsyncClient
from social_core.backends.github import GithubOAuth2
from social_core.backends.oauth import BaseOAuth2
from starlette.requests import Request

from fastapi_oauth2.client import OAuth2Client
from fastapi_oauth2.config import OAuth2Config
from fastapi_oauth2.middleware import OAuth2Backend
from fastapi_oauth2.middleware import OAuth2Middleware
from fastapi_oauth2.router import router as oauth2_router

app = FastAPI()
router = APIRouter()


@router.get("/test_backends")
async def _backends(request: Request):
    responses = []
    for module in os.listdir(backends.__path__[0]):
        try:
            module_instance = importlib.import_module("social_core.backends.%s" % module[:-3])
            backend_implementations = [
                attr for attr in module_instance.__dict__.values()
                if type(attr) is type and all([
                    issubclass(attr, BaseOAuth2),
                    attr is not BaseOAuth2,
                ])
            ]
            for backend_cls in backend_implementations:
                backend = OAuth2Backend(OAuth2Config(
                    clients=[
                        OAuth2Client(
                            backend=backend_cls,
                            client_id="test_client_id",
                            client_secret="test_client_secret",
                        )
                    ]
                ))
                responses.append(await backend.authenticate(request))
        except ImportError:
            continue
    return responses


app.include_router(router)
app.include_router(oauth2_router)
app.add_middleware(OAuth2Middleware, config={
    "allow_http": True,
    "clients": [
        OAuth2Client(
            backend=GithubOAuth2,
            client_id="test_id",
            client_secret="test_secret",
        ),
    ],
})


@pytest.mark.anyio
async def test_auth_redirect():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/oauth2/github/auth")
        assert response.status_code == 303  # Redirect


@pytest.mark.anyio
async def test_backends():
    async with AsyncClient(app=app, base_url="http://test") as client:
        assert all((await client.get("/test_backends")).json())
