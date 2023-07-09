import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from social_core.backends.github import GithubOAuth2

from fastapi_oauth2.client import OAuth2Client
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



def test_read_main():
    response = client.get("/")
    assert response.status_code == 404
