import os

from dotenv import load_dotenv
from social_core.backends.github import GithubOAuth2
from social_core.backends.google import GoogleOAuth2

from fastapi_oauth2.claims import Claims
from fastapi_oauth2.client import OAuth2Client
from fastapi_oauth2.config import OAuth2Config

load_dotenv()

oauth2_config = OAuth2Config(
    allow_http=True,
    jwt_secret=os.getenv("JWT_SECRET"),
    jwt_expires=os.getenv("JWT_EXPIRES"),
    jwt_algorithm=os.getenv("JWT_ALGORITHM"),
    clients=[
        OAuth2Client(
            backend=GithubOAuth2,
            client_id=os.getenv("OAUTH2_GITHUB_CLIENT_ID"),
            client_secret=os.getenv("OAUTH2_GITHUB_CLIENT_SECRET"),
            scope=["user:email"],
            claims=Claims(
                picture="avatar_url",
                identity=lambda user: f"{user.provider}:{user.id}",
            ),
        ),
        OAuth2Client(
            backend=GoogleOAuth2,
            client_id=os.getenv("OAUTH2_GOOGLE_CLIENT_ID"),
            client_secret=os.getenv("OAUTH2_GOOGLE_CLIENT_SECRET"),
            scope=["openid", "profile", "email"],
            claims=Claims(
                identity=lambda user: f"{user.provider}:{user.sub}",
            ),
        ),
    ]
)
