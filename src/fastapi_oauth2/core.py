import json
import random
import re
import string
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from urllib.parse import urljoin

import httpx
from oauthlib.oauth2 import WebApplicationClient
from social_core.backends.oauth import BaseOAuth2
from social_core.strategy import BaseStrategy
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import RedirectResponse

from .client import OAuth2Client


class OAuth2LoginError(HTTPException):
    """Raised when any login-related error occurs
    (such as when user is not verified or if there was an attempt for fake login)
    """


class OAuth2Strategy(BaseStrategy):
    def request_data(self, merge=True):
        return {}

    def absolute_uri(self, path=None):
        return path

    def get_setting(self, name):
        return None

    @staticmethod
    def get_json(url, method='GET', *args, **kwargs):
        return httpx.request(method, url, *args, **kwargs)


class OAuth2Core:
    """Base class (mixin) for all SSO providers"""

    client_id: str = None
    client_secret: str = None
    callback_url: Optional[str] = None
    scope: Optional[List[str]] = None
    backend: BaseOAuth2 = None
    _oauth_client: Optional[WebApplicationClient] = None

    authorization_endpoint: str = None
    token_endpoint: str = None

    def __init__(self, client: OAuth2Client) -> None:
        self.client_id = client.client_id
        self.client_secret = client.client_secret
        self.scope = client.scope or self.scope
        self.provider = client.backend.name
        self.backend = client.backend(OAuth2Strategy())
        self.authorization_endpoint = client.backend.AUTHORIZATION_URL
        self.token_endpoint = client.backend.ACCESS_TOKEN_URL

    @property
    def oauth_client(self) -> WebApplicationClient:
        if self._oauth_client is None:
            self._oauth_client = WebApplicationClient(self.client_id)
        return self._oauth_client

    def get_redirect_uri(self, request: Request) -> str:
        return urljoin(str(request.base_url), "/oauth2/%s/token" % self.provider)

    async def get_login_url(self, request: Request) -> Any:
        redirect_uri = self.get_redirect_uri(request)
        state = "".join([random.choice(string.ascii_letters) for _ in range(32)])
        return self.oauth_client.prepare_request_uri(
            self.authorization_endpoint, redirect_uri=redirect_uri, state=state, scope=self.scope
        )

    async def login_redirect(self, request: Request) -> RedirectResponse:
        return RedirectResponse(await self.get_login_url(request), 303)

    async def get_token_data(self, request: Request) -> Optional[Dict[str, Any]]:
        if not request.query_params.get("code"):
            raise OAuth2LoginError(400, "'code' parameter was not found in callback request")
        if not request.query_params.get("state"):
            raise OAuth2LoginError(400, "'state' parameter was not found in callback request")

        url = request.url
        scheme = "http" if request.auth.http else "https"
        current_url = re.sub(r"^https?", scheme, str(url))
        redirect_uri = self.get_redirect_uri(request)

        token_url, headers, content = self.oauth_client.prepare_token_request(
            self.token_endpoint,
            redirect_url=redirect_uri,
            authorization_response=current_url,
            code=request.query_params.get("code"),
            state=request.query_params.get("state"),
        )

        headers.update({
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
        })
        auth = httpx.BasicAuth(self.client_id, self.client_secret)
        async with httpx.AsyncClient() as session:
            response = await session.post(token_url, headers=headers, content=content, auth=auth)
            token = self.oauth_client.parse_request_body_response(json.dumps(response.json()))
            data = self.backend.user_data(token.get("access_token"))

        return {**data, "scope": self.scope}

    async def token_redirect(self, request: Request) -> RedirectResponse:
        token_data = await self.get_token_data(request)
        access_token = request.auth.jwt_create(token_data)
        response = RedirectResponse(request.base_url)
        response.set_cookie(
            "Authorization",
            value=f"Bearer {access_token}",
            max_age=request.auth.expires,
            expires=request.auth.expires,
            httponly=request.auth.http,
        )
        return response
