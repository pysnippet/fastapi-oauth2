from datetime import timedelta

from fastapi import APIRouter
from fastapi.responses import RedirectResponse
from starlette.requests import Request

from fastapi_oauth2.github import GitHubSSO
from .config import (
    CLIENT_ID,
    CLIENT_SECRET,
    CALLBACK_URL,
    JWT_EXPIRES,
    REDIRECT_URL,
)
from .utils import create_access_token

router = APIRouter()
sso = GitHubSSO(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    callback_url=CALLBACK_URL,
    allow_insecure_http=True,
)


@router.get("/auth/login")
async def login():
    return await sso.get_login_redirect()


@router.get("/auth/callback")
async def callback(request: Request):
    user = await sso.verify_and_process(request)
    expires_delta = timedelta(minutes=JWT_EXPIRES)
    access_token = create_access_token(
        data=dict(user), expires_delta=expires_delta
    )
    response = RedirectResponse(REDIRECT_URL)
    response.set_cookie(
        "Authorization",
        value=f"Bearer {access_token}",
        httponly=sso.allow_insecure_http,
        max_age=JWT_EXPIRES * 60,
        expires=JWT_EXPIRES * 60,
    )
    return response


@router.get("/auth/logout")
async def logout():
    response = RedirectResponse(REDIRECT_URL)
    response.delete_cookie("Authorization")
    return response
