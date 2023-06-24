from starlette.exceptions import HTTPException


class OAuth2LoginError(HTTPException):
    """Raised when any login-related error occurs
    (such as when user is not verified or if there was an attempt for fake login)
    """
