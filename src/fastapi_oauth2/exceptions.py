from starlette.exceptions import HTTPException


class OAuth2Error(HTTPException):
    ...


class OAuth2AuthenticationError(OAuth2Error):
    ...


class OAuth2BadCredentialsError(OAuth2Error):
    ...


class OAuth2InvalidRequestError(OAuth2Error):
    ...
