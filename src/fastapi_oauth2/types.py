from enum import Enum
from typing import Dict, TypedDict


class OAuth2Provider(str, Enum):
    github = "github"


class OAuth2Client(Dict[str, str]):
    client_id: str
    client_secret: str
    redirect_uri: str


class ConfigParams(TypedDict):
    allow_http: bool
    jwt_secret: str
    jwt_expires: int
    jwt_algorithm: str
    providers: Dict[OAuth2Provider, OAuth2Client]


class Config:
    allow_http: bool = False
    jwt_secret: str = ""
    jwt_expires: int = 900
    jwt_algorithm: str = "HS256"
    providers: Dict[OAuth2Provider, OAuth2Client] = {}

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
