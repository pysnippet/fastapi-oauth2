import urllib.parse

from fastapi import APIRouter
from fastapi import FastAPI
from fastapi import Request
from oauthlib.oauth2 import Server
from starlette.responses import RedirectResponse
from starlette.responses import Response

from .backend import TestOAuth2
from .validator import TestValidator


def get_idp():
    application = FastAPI()
    app_router = APIRouter()
    oauth2_server = Server(TestValidator())

    @app_router.get("/oauth/authorization")
    async def authorization(request: Request):
        uri = str(request.url)
        http_method = request.method
        headers = dict(request.headers)
        body_bytes = await request.body()
        body = body_bytes.decode("utf-8")

        scopes, credentials = oauth2_server.validate_authorization_request(uri, http_method, body, headers)
        uri = "http://idp/oauth/authorization?" + urllib.parse.urlencode({"scopes": ','.join(scopes), **credentials})
        headers, body, status_code = oauth2_server.create_authorization_response(uri, http_method, body, headers)

        if status_code == 302:
            location = headers.get('Location', '')
            return RedirectResponse(location, headers=headers, status_code=status_code)

        return Response(content=body, status_code=status_code)

    @app_router.post("/oauth/token")
    async def token(request: Request):
        uri = str(request.url)
        http_method = request.method
        headers = dict(request.headers)
        body_bytes = await request.body()
        body = body_bytes.decode("utf-8")

        headers, body, status_code = oauth2_server.create_token_response(uri, http_method, body, headers, {})

        return Response(content=body, headers=headers, status_code=status_code)

    application.include_router(app_router)
    return application
