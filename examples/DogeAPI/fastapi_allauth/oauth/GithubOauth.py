from typing import Optional, List

import requests

from .BaseOauth import BaseOauth
from ..secret_handler import SecretType

AUTH_URL = "https://github.com/login/oauth/authorize"
TOKEN_URL = "https://github.com/login/oauth/access_token"
USER_INFO_URL = "https://api.github.com/user"


class GithubOauth(BaseOauth):

    def __init__(
            self,
            provider: str = "GITHUB",
            client_id: str = "",
            client_secret: SecretType = "",
            redirect_uri: str = "",
            scope: Optional[List[str]] = None,
            refresh_token_url: Optional[str] = None,
            revoke_token_url: Optional[str] = None
    ):
        super().__init__(
            provider=provider,
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            authorize_url=AUTH_URL,
            access_token_url=TOKEN_URL,
            base_scope=scope,
            refresh_token_url=refresh_token_url,
            revoke_token_url=revoke_token_url
        )

    def get_userinfo(self, access_token: str):
        response = requests.get(USER_INFO_URL, headers={
            "authorization": f"Bearer {access_token}"})
        print("response", response.text)
        return response.json()

    def get_open_id(self, user_json: dict):
        return user_json["id"]
