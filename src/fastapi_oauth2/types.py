from typing import List, Optional, Type

from social_core.backends.oauth import BaseOAuth2


class OAuth2Client:
    backend: Type[BaseOAuth2]
    client_id: str
    client_secret: str
    redirect_uri: Optional[str]

    def __init__(
            self,
            *,
            backend: Type[BaseOAuth2],
            client_id: str,
            client_secret: str,
            redirect_uri: Optional[str] = None,
    ):
        self.backend = backend
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri


class OAuth2Config:
    allow_http: bool
    jwt_secret: str
    jwt_expires: int
    jwt_algorithm: str
    clients: List[OAuth2Client]

    def __init__(
            self,
            *,
            allow_http: bool = False,
            jwt_secret: str = "",
            jwt_expires: int = 900,
            jwt_algorithm: str = "HS256",
            clients: List[OAuth2Client] = None,
    ):
        self.allow_http = allow_http
        self.jwt_secret = jwt_secret
        self.jwt_expires = jwt_expires
        self.jwt_algorithm = jwt_algorithm
        self.clients = clients or []
