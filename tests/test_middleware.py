import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_middleware_on_authentication(get_app):
    async with AsyncClient(app=get_app(), base_url="http://test") as client:
        response = await client.get("/user")
        assert response.status_code == 403  # Forbidden

        await client.get("/auth")  # Simulate login

        response = await client.get("/user")
        assert response.status_code == 200  # OK


@pytest.mark.anyio
async def test_middleware_on_logout(get_app):
    async with AsyncClient(app=get_app(), base_url="http://test") as client:
        await client.get("/auth")  # Simulate login

        response = await client.get("/user")
        assert response.status_code == 200  # OK

        await client.get("/oauth2/logout")  # Perform logout

        response = await client.get("/user")
        assert response.status_code == 403  # Forbidden
