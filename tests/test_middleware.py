import pytest
from fastapi.responses import JSONResponse
from httpx import AsyncClient
from jose import jwt


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
async def test_middleware_do_not_interfere_user_errors(get_app):
    app = get_app()

    @app.get("/unexpected_error")
    def my_entry_point():
        raise NameError  # Intended code error

    async with AsyncClient(app=app, base_url="http://test") as client:
        with pytest.raises(NameError):
            await client.get("/unexpected_error")


@pytest.mark.anyio
async def test_middleware_ignores_custom_exceptions(get_app):
    class MyCustomException(Exception):
        pass

    app = get_app()

    @app.get("/custom_exception")
    def my_entry_point():
        raise MyCustomException()

    async with AsyncClient(app=app, base_url="http://test") as client:
        with pytest.raises(MyCustomException):
            await client.get("/custom_exception")


@pytest.mark.anyio
async def test_middleware_ignores_handled_custom_exceptions(get_app):
    class MyHandledException(Exception):
        pass

    app = get_app()

    @app.exception_handler(MyHandledException)
    async def unicorn_exception_handler(request, exc):
        return JSONResponse(
            status_code=418,
            content={"details": "I am a custom Teapot!"},
        )

    @app.get("/handled_exception")
    def my_entry_point():
        raise MyHandledException()

    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/handled_exception")
        assert response.status_code == 418  # I am a teapot!
        assert response.json() == {"details": "I am a custom Teapot!"}


@pytest.mark.anyio
async def test_middleware_reports_invalid_jwt(get_app):
    async with AsyncClient(app=get_app(with_ssr=False), base_url="http://test") as client:
        # Insert a bad token instead
        badtoken = jwt.encode({"bad": "token"}, "badsecret", "HS256")
        client.cookies.update(dict(Authorization=f"Bearer: {badtoken}"))

        response = await client.get("/user")
        assert response.status_code == 400
        assert response.text == "Signature verification failed."
