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

@pytest.mark.anyio
async def test_middleware_do_not_interfer_user_errors(get_app):
    app=get_app()
    @app.get('/unexpected_error')
    def unexpected():
        undefined_id # Intended code error

    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/unexpected_error")
        assert response.status_code == 500  # Internal server error

@pytest.mark.anyio
async def test_middleware_ignores_custom_exceptions(get_app):
    class MyCustomException(Exception): pass
    app=get_app()
    @app.get('/custom_exception')
    def custom_exception():
        raise MyCustomException()

    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/custom_exception")
        assert response.status_code == 500  # Internal server error

@pytest.mark.anyio
async def test_middleware_ignores_handled_custom_exceptions(get_app):
    class MyCustomException(Exception): pass
    app=get_app()
    @app.exception_handler(MyCustomException)
    async def unicorn_exception_handler(request, exc):
        return JSONResponse(
            status_code=418,
            content={"message": f"I am a Teapot!"},
        )

    @app.get('/custom_exception')
    def custom_exception():
        raise MyCustomException()

    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/custom_exception")
        assert response.status_code == 418 # I am a teapot!
