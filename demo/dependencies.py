from typing import Optional

from fastapi import Depends, HTTPException
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.security import OAuth2
from fastapi.security.utils import get_authorization_scheme_param
from jose import jwt, JWTError
from starlette.requests import Request
from starlette.status import HTTP_403_FORBIDDEN

from fastapi_oauth2.config import JWT_SECRET, JWT_ALGORITHM


class OAuth2PasswordBearerCookie(OAuth2):
    def __init__(
            self,
            tokenUrl: str,
            scheme_name: str = None,
            scopes: dict = None,
            auto_error: bool = True,
    ):
        flows = OAuthFlowsModel(password={"tokenUrl": tokenUrl, "scopes": scopes or {}})
        super().__init__(flows=flows, scheme_name=scheme_name, auto_error=auto_error)

    async def __call__(self, request: Request) -> Optional[str]:
        scheme, param = get_authorization_scheme_param(request.headers.get("Authorization"))
        authorization = scheme.lower() == "bearer"
        if not authorization:
            scheme, param = get_authorization_scheme_param(request.cookies.get("Authorization"))
            authorization = scheme.lower() == "bearer"

        if not authorization:
            if self.auto_error:
                raise HTTPException(
                    status_code=HTTP_403_FORBIDDEN, detail="Not authenticated"
                )
            else:
                return None
        return param


oauth2_scheme = OAuth2PasswordBearerCookie(tokenUrl="/token")


async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except JWTError:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="Could not validate credentials"
        )
