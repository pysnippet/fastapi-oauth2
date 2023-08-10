import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_auth_redirect(app):
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/oauth2/github/auth")
        assert response.status_code == 303  # Redirect


@pytest.mark.anyio
async def test_token_redirect(app):
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/oauth2/github/token")
        assert response.status_code == 400  # Bad Request

        response = await client.get("/oauth2/github/token?state=test&code=test")
        assert response.status_code == 400  # Bad Request


@pytest.mark.anyio
async def test_logout_redirect(app):
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/oauth2/logout")
        assert response.status_code == 307  # Redirect
