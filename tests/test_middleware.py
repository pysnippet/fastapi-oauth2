import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_logout_redirect():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/oauth2/logout")
        assert response.status_code == 307  # Redirect


@pytest.mark.anyio
async def test_authentication():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/user")
        assert response.status_code == 403  # Forbidden

        await client.get("/auth")  # Simulate login

        response = await client.get("/user")
        assert response.status_code == 200  # OK


@pytest.mark.anyio
async def test_logout():
    async with AsyncClient(app=app, base_url="http://test") as client:
        await client.get("/auth")  # Simulate login

        response = await client.get("/user")
        assert response.status_code == 200  # OK

        await client.get("/oauth2/logout")  # Perform logout

        response = await client.get("/user")
        assert response.status_code == 403  # Forbidden
