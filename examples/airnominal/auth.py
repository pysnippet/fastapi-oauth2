import os
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter
from fastapi import Depends, HTTPException
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.responses import RedirectResponse
from fastapi.security import HTTPBearer
from fastapi.security import OAuth2
from fastapi.security.base import SecurityBase
from fastapi.security.utils import get_authorization_scheme_param
from fastapi_sso.sso.github import GithubSSO
from jose import jwt
from pydantic import BaseModel
from starlette.requests import Request
from starlette.status import HTTP_403_FORBIDDEN

from config import CLIENT_ID, CLIENT_SECRET, redirect_url, SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, \
    redirect_url_main_page

router = APIRouter()

# config for github SSO
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

sso = GithubSSO(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=redirect_url,
    allow_insecure_http=True,
)

security = HTTPBearer()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str = None


class User(BaseModel):
    username: str
    email: str = None
    full_name: str = None
    disabled: bool = None


class UserInDB(User):
    hashed_password: str


class OAuth2PasswordBearerCookie(OAuth2):
    def __init__(
            self,
            tokenUrl: str,
            scheme_name: str = None,
            scopes: dict = None,
            auto_error: bool = True,
    ):
        if not scopes:
            scopes = {}
        flows = OAuthFlowsModel(password={"tokenUrl": tokenUrl, "scopes": scopes})
        super().__init__(flows=flows, scheme_name=scheme_name, auto_error=auto_error)

    async def __call__(self, request: Request) -> Optional[str]:
        header_authorization: str = request.headers.get("Authorization")
        cookie_authorization: str = request.cookies.get("Authorization")

        header_scheme, header_param = get_authorization_scheme_param(
            header_authorization
        )
        cookie_scheme, cookie_param = get_authorization_scheme_param(
            cookie_authorization
        )

        if header_scheme.lower() == "bearer":
            authorization = True
            scheme = header_scheme
            param = header_param

        elif cookie_scheme.lower() == "bearer":
            authorization = True
            scheme = cookie_scheme
            param = cookie_param

        else:
            authorization = False

        if not authorization or scheme.lower() != "bearer":
            if self.auto_error:
                raise HTTPException(
                    status_code=HTTP_403_FORBIDDEN, detail="Not authenticated"
                )
            else:
                return None
        return param


class BasicAuth(SecurityBase):
    def __init__(self, scheme_name: str = None, auto_error: bool = True):
        self.scheme_name = scheme_name or self.__class__.__name__
        self.auto_error = auto_error

    async def __call__(self, request: Request) -> Optional[str]:
        authorization: str = request.headers.get("Authorization")
        scheme, param = get_authorization_scheme_param(authorization)
        if not authorization or scheme.lower() != "basic":
            if self.auto_error:
                raise HTTPException(
                    status_code=HTTP_403_FORBIDDEN, detail="Not authenticated"
                )
            else:
                return None
        return param


basic_auth = BasicAuth(auto_error=False)

oauth2_scheme = OAuth2PasswordBearerCookie(tokenUrl="/token")


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=HTTP_403_FORBIDDEN, detail="Could not validate credentials"
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except PyJWTError:
        raise credentials_exception


@router.get("/auth/login")
async def auth_init():
    """Initialize auth and redirect"""
    return await sso.get_login_redirect()


@router.get("/auth/callback")
async def auth_callback(request: Request):
    """Verify login"""
    user = await sso.verify_and_process(request)
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data=dict(user), expires_delta=access_token_expires
    )
    print(dict(user))
    response = RedirectResponse(redirect_url_main_page)
    response.set_cookie(
        "Authorization",
        value=f"Bearer {access_token}",
        httponly=True,
        max_age=1800,
        expires=1800,
    )
    return response


@router.get("/auth/logout")
async def auth_logout():
    response = RedirectResponse(redirect_url_main_page)
    response.delete_cookie("Authorization")
    return response


@router.get("/auth/status")
async def auth_status(user=Depends(get_current_user)):
    return {
        "ok": True,
        "user": user,
    }
