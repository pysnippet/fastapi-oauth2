import secrets
import string
import time
from collections import OrderedDict
from typing import Optional
from typing import Tuple

from jose.exceptions import JOSEError
from starlette.requests import Request
from starlette.responses import Response


class CSRFStateBackend:
    @staticmethod
    def generate_state(request: Request) -> str:
        request.state.oauth2_state = "".join([secrets.choice(string.ascii_letters) for _ in range(32)])
        if request.query_params.get("state"):
            request.state.oauth2_state = request.query_params["state"]
        return request.state.oauth2_state

    def store_state(self, request: Request, response: Optional[Response] = None) -> None:
        """Called after the state has been generated during the redirect process.
        Response will only be available if SSR is enabled."""
        raise NotImplementedError

    def read_state(self, request: Request) -> Optional[str]:
        """Called during the callback process to retrieve the expected state."""
        raise NotImplementedError

    def clear_state(self, request: Request, response: Response) -> None:
        """Called after the state has been validated during the callback process."""
        raise NotImplementedError


class InMemoryStateBackend(CSRFStateBackend):
    """Tracks pending states in memory, so multiple flows can be in flight at once
    within a single process. Does not work across multiple workers/processes, so it
    shouldn't be used in production deployments that run more than one process.

    When a response is available (SSR), every state is bound to the browser that
    started the flow through a random binding cookie, so a callback URL captured by
    one client cannot be replayed by another (login CSRF). Without a response
    (non-SSR), the state cannot be bound on the server and the client application
    is responsible for generating and verifying it."""

    def __init__(
        self,
        max_age: int = 600,
        max_pending: int = 1000,
        cookie_name: str = "CSRFStateBinding",
    ) -> None:
        self.max_age = max_age
        self.max_pending = max_pending
        self.cookie_name = cookie_name
        self._states: "OrderedDict[str, Tuple[float, Optional[str]]]" = OrderedDict()

    def store_state(self, request: Request, response: Optional[Response] = None) -> None:
        binding = None
        if response is not None:
            # Reuse the browser's binding so concurrent flows (e.g. several tabs) keep working
            binding = request.cookies.get(self.cookie_name) or secrets.token_urlsafe(32)
            response.set_cookie(
                self.cookie_name,
                value=binding,
                max_age=self.max_age,
                secure=not request.auth.http,
                httponly=True,
                samesite=request.auth.same_site,
            )
        while len(self._states) >= self.max_pending:
            self._states.popitem(last=False)
        self._states[request.state.oauth2_state] = (time.time() + self.max_age, binding)

    def read_state(self, request: Request) -> Optional[str]:
        state = request.query_params.get("state")
        entry = self._states.get(state)
        if entry is None:
            return None
        expires, binding = entry
        if expires < time.time():
            return None
        if binding is not None and not secrets.compare_digest(
            binding.encode(), request.cookies.get(self.cookie_name, "").encode(),
        ):
            return None
        return state

    def clear_state(self, request: Request, response: Response) -> None:
        self._states.pop(request.query_params.get("state"), None)


class CookieStateBackend(CSRFStateBackend):
    def __init__(
        self,
        cookie_name: str = "CSRFState",
        max_age: int = 600,  # 10 minutes
    ):
        self.cookie_name = cookie_name
        self.max_age = max_age

    def store_state(self, request: Request, response: Optional[Response] = None) -> None:
        if not response:
            raise RuntimeError("CookieStateBackend can only be used with SSR enabled.")

        response.set_cookie(
            self.cookie_name,
            value=request.auth.jwt_encode({
                "state": request.state.oauth2_state,
                "exp": int(time.time()) + self.max_age,
            }),
            max_age=self.max_age,
            secure=not request.auth.http,
            httponly=True,
            samesite=request.auth.same_site,
        )

    def read_state(self, request: Request) -> Optional[str]:
        token = request.cookies.get(self.cookie_name)
        if not token:
            return None
        try:
            return request.auth.jwt_decode(token).get("state")
        except JOSEError:
            return None

    def clear_state(self, request: Request, response: Response) -> None:
        response.delete_cookie(self.cookie_name)
