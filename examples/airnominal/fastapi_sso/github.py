"""GitHub SSO Oauth Helper class"""

from .base import DiscoveryDocument, SSOBase


class GithubSSO(SSOBase):
    """Class providing login via GitHub SSO"""

    provider = "github"
    scope = ["user:email"]
    additional_headers = {"accept": "application/json"}

    async def get_discovery_document(self) -> DiscoveryDocument:
        return {
            "authorization_endpoint": "https://github.com/login/oauth/authorize",
            "token_endpoint": "https://github.com/login/oauth/access_token",
            "userinfo_endpoint": "https://api.github.com/user",
        }

    @classmethod
    async def openid_from_response(cls, response: dict) -> dict:
        return {**response, "provider": cls.provider}
