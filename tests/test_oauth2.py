import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_oauth2_basic_flow(get_app):
    async with AsyncClient(app=get_app(), base_url="http://test") as client:
        response = await client.get("/user")
        assert response.status_code == 403
        response = await client.get("/oauth2/test/auth")
        response = await client.get(response.headers.get("location"))
        await client.get(response.headers.get("location"))
        response = await client.get("/user")
        assert response.status_code == 200
