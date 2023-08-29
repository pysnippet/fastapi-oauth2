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
from oauthlib.oauth2.rfc6749.errors import CustomOAuth2Error
from social_core.backends.oauth import BaseOAuth2
from social_core.strategy import BaseStrategy
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import RedirectResponse

from .claims import Claims
from .client import OAuth2Client


class OAuth2LoginError(HTTPException):
    """Raised when any login-related error occurs."""


class OAuth2Strategy(BaseStrategy):
    """Dummy strategy for using the `BaseOAuth2.user_data` method."""

    def request_data(self, merge=True) -> Dict[str, Any]:
        return {}

    def absolute_uri(self, path=None) -> str:
        return path

    def get_setting(self, name) -> Any:
        """Mocked setting method."""

    @staticmethod
    def get_json(url, method='GET', *args, **kwargs) -> httpx.Response:
        return httpx.request(method, url, *args, **kwargs)


class OAuth2Core:
    """OAuth2 flow handler of a certain provider."""

    client_id: str = None
    client_secret: str = None
    scope: Optional[List[str]] = None
    claims: Optional[Claims] = None
    provider: str = None
    redirect_uri: str = None
    backend: BaseOAuth2 = None
    _oauth_client: Optional[WebApplicationClient] = None

    authorization_endpoint: str = None
    token_endpoint: str = None

    def __init__(self, client: OAuth2Client) -> None:
        self.client_id = client.client_id
        self.client_secret = client.client_secret
        self.scope = client.scope
        self.claims = client.claims
        self.provider = client.backend.name
        self.redirect_uri = client.redirect_uri
        self.backend = client.backend(OAuth2Strategy())
        self.authorization_endpoint = client.backend.AUTHORIZATION_URL
        self.token_endpoint = client.backend.ACCESS_TOKEN_URL
        self._oauth_client = WebApplicationClient(self.client_id)

    @property
    def access_token(self) -> str:
        return self._oauth_client.access_token

    def get_redirect_uri(self, request: Request) -> str:
        return urljoin(str(request.base_url), "/oauth2/%s/token" % self.provider)

    async def login_redirect(self, request: Request) -> RedirectResponse:
        redirect_uri = self.get_redirect_uri(request)
        state = "".join([random.choice(string.ascii_letters) for _ in range(32)])
        return RedirectResponse(str(self._oauth_client.prepare_request_uri(
            self.authorization_endpoint,
            state=state,
            scope=self.scope,
            **request.query_params,
            redirect_uri=redirect_uri,
        )), 303)

    async def token_redirect(self, request: Request) -> RedirectResponse:
        if not request.query_params.get("code"):
            raise OAuth2LoginError(400, "'code' parameter was not found in callback request")
        if not request.query_params.get("state"):
            raise OAuth2LoginError(400, "'state' parameter was not found in callback request")

        redirect_uri = self.get_redirect_uri(request)
        scheme = "http" if request.auth.http else "https"
        authorization_response = re.sub(r"^https?", scheme, str(request.url))

        token_url, headers, content = self._oauth_client.prepare_token_request(
            self.token_endpoint,
            **request.query_params,
            redirect_url=redirect_uri,
            authorization_response=authorization_response,
        )

        headers.update({
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
        })
        auth = httpx.BasicAuth(self.client_id, self.client_secret)
        async with httpx.AsyncClient() as session:
            response = await session.post(token_url, headers=headers, content=content, auth=auth)
            try:
                self._oauth_client.parse_request_body_response(json.dumps(response.json()))
                token_data = self.standardize(self.backend.user_data(self.access_token))
                access_token = request.auth.jwt_create(token_data)
            except (CustomOAuth2Error, Exception) as e:
                raise OAuth2LoginError(400, str(e))

        response = RedirectResponse(self.redirect_uri or request.base_url)
        response.set_cookie(
            "Authorization",
            value=f"Bearer {access_token}",
            max_age=request.auth.expires,
            expires=request.auth.expires,
            httponly=request.auth.http,
        )
        return response

    def standardize(self, data: Dict[str, Any]) -> Dict[str, Any]:
        data["provider"] = self.provider
        data["scope"] = self.scope
        return data
