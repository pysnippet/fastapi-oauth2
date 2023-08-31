import json
import urllib.parse

from fastapi import FastAPI, Request, Response
from oauthlib.oauth2 import Server
from starlette.responses import RedirectResponse

from validator import MyRequestValidator

app = FastAPI()
oauth2_server = Server(MyRequestValidator())


@app.get("/auth")
async def auth(request: Request):
    uri = str(request.url)
    http_method = request.method
    headers = dict(request.headers)
    body_bytes = await request.body()
    body = body_bytes.decode("utf-8")

    scopes, credentials = oauth2_server.validate_authorization_request(uri, http_method, body, headers)
    uri = "/auth?" + urllib.parse.urlencode({"scopes": ','.join(scopes), **credentials})
    headers, body, status_code = oauth2_server.create_authorization_response(uri, http_method, body, headers)

    if status_code == 302:
        location = headers.get('Location', '')
        return RedirectResponse(location, headers=headers, status_code=status_code)

    return Response(content=body, status_code=status_code)


@app.post("/token")
async def token(request: Request):
    uri = str(request.url)
    http_method = request.method
    headers = dict(request.headers)
    body_bytes = await request.body()
    body = body_bytes.decode("utf-8")

    headers, body, status_code = oauth2_server.create_token_response(uri, http_method, body, headers, {})

    return Response(content=json.dumps({
        **json.loads(body),
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c",
    }), status_code=status_code)
