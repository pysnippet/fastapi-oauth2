from datetime import timedelta

from fastapi import APIRouter
from fastapi import Depends
from fastapi.responses import RedirectResponse
from starlette.requests import Request

from fastapi_oauth2.github import GitHubSSO
from .config import (
    CLIENT_ID,
    CLIENT_SECRET,
    redirect_url,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    redirect_url_main_page,
)
from .dependencies import get_current_user
from .utils import create_access_token

router = APIRouter()
sso = GitHubSSO(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=redirect_url,
    allow_insecure_http=True,
)


@router.get("/user")
def user(current_user=Depends(get_current_user)):
    return current_user


@router.post("/token")
def token(request: Request):
    return request.cookies.get("Authorization")


@router.get("/auth/login")
async def auth_init():
    return await sso.get_login_redirect()


@router.get("/auth/callback")
async def auth_callback(request: Request):
    user = await sso.verify_and_process(request)
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data=dict(user), expires_delta=access_token_expires
    )
    response = RedirectResponse(redirect_url_main_page)
    response.set_cookie(
        "Authorization",
        value=f"Bearer {access_token}",
        httponly=sso.allow_insecure_http,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        expires=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
    return response


@router.get("/auth/logout")
async def auth_logout():
    response = RedirectResponse(redirect_url_main_page)
    response.delete_cookie("Authorization")
    return response
