import json
import re
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from urllib.parse import urljoin

import httpx
from oauthlib.oauth2 import WebApplicationClient
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import RedirectResponse

from .client import OAuth2Client


class OAuth2LoginError(HTTPException):
    """Raised when any login-related error occurs
    (such as when user is not verified or if there was an attempt for fake login)
    """


class OAuth2Core:
    """Base class (mixin) for all SSO providers"""

    client_id: str = None
    client_secret: str = None
    callback_url: Optional[str] = None
    allow_http: bool = False
    scope: Optional[List[str]] = None
    state: Optional[str] = None
    _oauth_client: Optional[WebApplicationClient] = None
    additional_headers: Optional[Dict[str, Any]] = None

    authorization_endpoint: str = None
    token_endpoint: str = None
    userinfo_endpoint: str = None

    def __init__(self, client: OAuth2Client) -> None:
        self.client_id = client.client_id
        self.client_secret = client.client_secret
        self.scope = client.scope or self.scope
        self.provider = client.backend.name
        self.authorization_endpoint = client.backend.AUTHORIZATION_URL
        self.token_endpoint = client.backend.ACCESS_TOKEN_URL
        self.userinfo_endpoint = "https://api.github.com/user"
        self.additional_headers = {"Content-Type": "application/x-www-form-urlencoded", "Accept": "application/json"}

    @property
    def oauth_client(self) -> WebApplicationClient:
        if self._oauth_client is None:
            self._oauth_client = WebApplicationClient(self.client_id)
        return self._oauth_client

    def get_redirect_uri(self, request: Request) -> str:
        return urljoin(str(request.base_url), "/oauth2/%s/token" % self.provider)

    async def get_login_url(
            self,
            request: Request,
            *,
            params: Optional[Dict[str, Any]] = None,
            state: Optional[str] = None,
    ) -> Any:
        self.state = state
        params = params or {}
        redirect_uri = self.get_redirect_uri(request)
        return self.oauth_client.prepare_request_uri(
            self.authorization_endpoint, redirect_uri=redirect_uri, state=state, scope=self.scope, **params
        )

    async def login_redirect(
            self,
            request: Request,
            *,
            params: Optional[Dict[str, Any]] = None,
            state: Optional[str] = None,
    ) -> RedirectResponse:
        login_uri = await self.get_login_url(request, params=params, state=state)
        return RedirectResponse(login_uri, 303)

    async def get_token_data(
            self,
            request: Request,
            *,
            params: Optional[Dict[str, Any]] = None,
            headers: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        params = params or {}
        additional_headers = headers or {}
        additional_headers.update(self.additional_headers or {})
        if not request.query_params.get("code"):
            raise OAuth2LoginError(400, "'code' parameter was not found in callback request")
        if self.state != request.query_params.get("state"):
            raise OAuth2LoginError(400, "'state' parameter does not match")

        url = request.url
        scheme = "http" if self.allow_http else "https"
        current_url = re.sub(r"^https?", scheme, str(url))
        redirect_uri = self.get_redirect_uri(request)

        token_url, headers, content = self.oauth_client.prepare_token_request(
            self.token_endpoint,
            redirect_url=redirect_uri,
            authorization_response=current_url,
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

        return {**content, "scope": self.scope}

    async def token_redirect(
            self,
            request: Request,
            *,
            params: Optional[Dict[str, Any]] = None,
            headers: Optional[Dict[str, Any]] = None,
    ) -> RedirectResponse:
        token_data = await self.get_token_data(request, params=params, headers=headers)
        access_token = request.auth.jwt_create(token_data)
        response = RedirectResponse(request.base_url)
        response.set_cookie(
            "Authorization",
            value=f"Bearer {access_token}",
            httponly=self.allow_http,
            max_age=request.auth.expires,
            expires=request.auth.expires,
        )
        return response
