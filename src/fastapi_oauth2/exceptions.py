from starlette.exceptions import HTTPException


class OAuth2LoginError(HTTPException):
    """Raised when any login-related error occurs."""
