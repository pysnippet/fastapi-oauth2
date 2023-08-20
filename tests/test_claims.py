import pytest
from fastapi import APIRouter
from fastapi import Request
from httpx import AsyncClient

from fastapi_oauth2.claims import Claims


@pytest.mark.anyio
async def test_permanent_claims_mapping(get_app):
    app = get_app()
    router = APIRouter()

    @router.get("/test_claims")
    def test_claims(request: Request):
        user = request.user.use_claims(Claims())  # use default claims mapping
        assert user.display_name == "John Doe"
        assert user.identity == "1234567890"
        assert user.picture == ""
        assert user.email == ""

    app.include_router(router)

    async with AsyncClient(app=app, base_url="http://test") as client:
        await client.get("/auth")  # Simulate login
        await client.get("/test_claims")


@pytest.mark.anyio
async def test_custom_claims_mapping(get_app):
    app = get_app()
    router = APIRouter()

    @router.get("/test_claims")
    def test_claims(request: Request):
        user = request.user.use_claims(Claims(
            picture="image",
            email=lambda u: u.emails[0],
            identity=lambda u: f"{u.provider}:{u.sub}",
            is_popular=lambda u: u.followers > 100,
        ))  # use custom claims mapping
        assert user.display_name == "John Doe"
        assert user.identity == "github:1234567890"
        assert user.picture == "https://example.com/john.doe.png"
        assert user.email == "john.doe@test.py"
        assert not user.is_popular

    app.include_router(router)

    async with AsyncClient(app=app, base_url="http://test") as client:
        await client.get("/auth")  # Simulate login
        await client.get("/test_claims")
