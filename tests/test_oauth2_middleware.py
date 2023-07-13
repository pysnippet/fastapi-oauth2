import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from social_core.backends.github import GithubOAuth2

from fastapi_oauth2.client import OAuth2Client
from fastapi_oauth2.core import OAuth2Core
from fastapi_oauth2.middleware import OAuth2Middleware
from fastapi_oauth2.router import router as oauth2_router

app = FastAPI()

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
async def test_core_init(backends):
    for backend in backends:
        try:
            OAuth2Core(OAuth2Client(
                backend=backend,
                client_id="test_client_id",
                client_secret="test_client_secret",
            ))
        except (NotImplementedError, Exception):
            assert False
