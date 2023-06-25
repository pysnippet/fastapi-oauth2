from fastapi import APIRouter
from fastapi.responses import RedirectResponse
from starlette.requests import Request

from fastapi_oauth2.github import GitHubOAuth2
from .config import (
    OAUTH2_CLIENT_ID,
    OAUTH2_CLIENT_SECRET,
    OAUTH2_CALLBACK_URL,
)

router = APIRouter(prefix="/oauth2")
oauth2 = GitHubOAuth2(
    client_id=OAUTH2_CLIENT_ID,
    client_secret=OAUTH2_CLIENT_SECRET,
    callback_url=OAUTH2_CALLBACK_URL,
    allow_insecure_http=True,
)


@router.get("/{provider}/auth")
async def login(provider: str):
    print(provider)
    return await oauth2.login_redirect()


@router.get("/token")
async def token(request: Request):
    return await oauth2.token_redirect(request)


@router.get("/logout")
async def logout(request: Request):
    response = RedirectResponse(request.base_url)
    response.delete_cookie("Authorization")
    return response
