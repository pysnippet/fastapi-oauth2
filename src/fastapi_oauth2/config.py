import os
from typing import List
from typing import Union
from typing import Optional

from .client import OAuth2Client
from .csrf_state import CookieStateBackend
from .csrf_state import CSRFStateBackend


class OAuth2Config:
    """Configuration class of the authentication middleware."""

    enable_ssr: bool
    allow_http: bool
    same_site: str
    jwt_secret: str
    jwt_expires: int
    jwt_algorithm: str
    clients: List[OAuth2Client]
    state_backend: Optional[CSRFStateBackend]

    def __init__(
            self,
            *,
            enable_ssr: bool = True,
            allow_http: bool = False,
            same_site: str = "lax",
            jwt_secret: str = "",
            jwt_expires: Union[int, str] = 900,
            jwt_algorithm: str = "HS256",
            clients: List[OAuth2Client] = None,
            state_backend: Optional[CSRFStateBackend] = None,
    ) -> None:
        if allow_http:
            os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
        if isinstance(state_backend, CookieStateBackend) and not enable_ssr:
            raise ValueError("CookieStateBackend requires enable_ssr to be True")
        self.enable_ssr = enable_ssr
        self.allow_http = allow_http
        self.same_site = same_site
        self.jwt_secret = jwt_secret
        self.jwt_expires = int(jwt_expires)
        self.jwt_algorithm = jwt_algorithm
        self.clients = clients or []
        self.state_backend = state_backend
