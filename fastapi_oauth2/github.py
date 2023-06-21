from .base import SSOBase


class GithubSSO(SSOBase):
    """Class providing login via GitHub SSO"""

    provider = "github"
    scope = ["user:email"]
    additional_headers = {"accept": "application/json"}

    authorization_endpoint = "https://github.com/login/oauth/authorize"
    token_endpoint = "https://github.com/login/oauth/access_token"
    userinfo_endpoint = "https://api.github.com/user"
