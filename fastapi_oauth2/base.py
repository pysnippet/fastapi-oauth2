import json
import os
import re
from typing import Any, Dict, List, Optional

import httpx
from oauthlib.oauth2 import WebApplicationClient
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import RedirectResponse

from .config import JWT_EXPIRES, OAUTH2_REDIRECT_URL
from .utils import create_access_token


class OAuth2LoginError(HTTPException):
    """Raised when any login-related error occurs
    (such as when user is not verified or if there was an attempt for fake login)
    """


class OAuth2Base:
    """Base class (mixin) for all SSO providers"""

    client_id: str = None
    client_secret: str = None
    callback_url: Optional[str] = None
    allow_insecure_http: bool = False
    scope: Optional[List[str]] = None
    state: Optional[str] = None
    _oauth_client: Optional[WebApplicationClient] = None
    additional_headers: Optional[Dict[str, Any]] = None

    authorization_endpoint: str = None
    token_endpoint: str = None
    userinfo_endpoint: str = None

    def __init__(
            self,
            client_id: str,
            client_secret: str,
            callback_url: Optional[str] = None,
            allow_insecure_http: bool = False,
            scope: Optional[List[str]] = None,
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.callback_url = callback_url
        self.allow_insecure_http = allow_insecure_http
        if allow_insecure_http:
            os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
        self.scope = scope or self.scope

    @property
    def oauth_client(self) -> WebApplicationClient:
        if self._oauth_client is None:
            self._oauth_client = WebApplicationClient(self.client_id)
        return self._oauth_client

    @property
    def access_token(self) -> Optional[str]:
        return self.oauth_client.access_token

    @property
    def refresh_token(self) -> Optional[str]:
        return self.oauth_client.refresh_token

    async def get_login_url(
            self,
            *,
            redirect_uri: Optional[str] = None,
            params: Optional[Dict[str, Any]] = None,
            state: Optional[str] = None,
    ) -> Any:
        self.state = state
        params = params or {}
        redirect_uri = redirect_uri or self.callback_url
        if redirect_uri is None:
            raise ValueError("callback_url must be provided, either at construction or request time")
        return self.oauth_client.prepare_request_uri(
            self.authorization_endpoint, redirect_uri=redirect_uri, state=state, scope=self.scope, **params
        )

    async def login_redirect(
            self,
            *,
            redirect_uri: Optional[str] = None,
            params: Optional[Dict[str, Any]] = None,
            state: Optional[str] = None,
    ) -> RedirectResponse:
        login_uri = await self.get_login_url(redirect_uri=redirect_uri, params=params, state=state)
        return RedirectResponse(login_uri, 303)

    async def get_token_data(
            self,
            request: Request,
            *,
            params: Optional[Dict[str, Any]] = None,
            headers: Optional[Dict[str, Any]] = None,
            redirect_uri: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        params = params or {}
        additional_headers = headers or {}
        additional_headers.update(self.additional_headers or {})
        if not request.query_params.get("code"):
            raise OAuth2LoginError(400, "'code' parameter was not found in callback request")
        if self.state != request.query_params.get("state"):
            raise OAuth2LoginError(400, "'state' parameter does not match")

        url = request.url
        scheme = "http" if self.allow_insecure_http else "https"
        current_path = f"{scheme}://{url.netloc}{url.path}"
        current_path = re.sub(r"^https?", scheme, current_path)
        current_url = re.sub(r"^https?", scheme, str(url))

        token_url, headers, content = self.oauth_client.prepare_token_request(
            self.token_endpoint,
            authorization_response=current_url,
            redirect_url=redirect_uri or self.callback_url or current_path,
            code=request.query_params.get("code"),
            **params,
        )

        headers.update(additional_headers)
        auth = httpx.BasicAuth(self.client_id, self.client_secret)
        async with httpx.AsyncClient() as session:
            response = await session.post(token_url, headers=headers, content=content, auth=auth)
            self.oauth_client.parse_request_body_response(json.dumps(response.json()))

            url, headers, _ = self.oauth_client.add_token(self.userinfo_endpoint)
            response = await session.get(url, headers=headers)
            content = response.json()

        return content

    async def token_redirect(
            self,
            request: Request,
            *,
            params: Optional[Dict[str, Any]] = None,
            headers: Optional[Dict[str, Any]] = None,
            redirect_uri: Optional[str] = None,
    ) -> RedirectResponse:
        token_data = await self.get_token_data(request, params=params, headers=headers, redirect_uri=redirect_uri)
        access_token = create_access_token(token_data)
        response = RedirectResponse(OAUTH2_REDIRECT_URL)
        response.set_cookie(
            "Authorization",
            value=f"Bearer {access_token}",
            httponly=self.allow_insecure_http,
            max_age=JWT_EXPIRES * 60,
            expires=JWT_EXPIRES * 60,
        )
        return response
