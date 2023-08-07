import pytest
from fastapi import APIRouter
from fastapi import Depends
from fastapi import FastAPI
from fastapi import Request
from httpx import AsyncClient
from social_core.backends.github import GithubOAuth2
from starlette.responses import Response

from fastapi_oauth2.client import OAuth2Client
from fastapi_oauth2.middleware import OAuth2Middleware
from fastapi_oauth2.router import router as oauth2_router
from fastapi_oauth2.security import OAuth2

app = FastAPI()
oauth2 = OAuth2()
app_router = APIRouter()


@app_router.get("/user")
def user(request: Request, _: str = Depends(oauth2)):
    return request.user


@app_router.get("/auth")
def auth(request: Request):
    access_token = request.auth.jwt_create({
        "name": "test",
        "sub": "test",
        "id": "test",
    })
    response = Response()
    response.set_cookie(
        "Authorization",
        value=f"Bearer {access_token}",
        max_age=request.auth.expires,
        expires=request.auth.expires,
        httponly=request.auth.http,
    )
    return response


app.include_router(app_router)
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
async def test_authenticated_request():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/user")
        assert response.status_code == 403  # Forbidden

        await client.get("/auth")  # Simulate login

        response = await client.get("/user")
        assert response.status_code == 200  # OK
