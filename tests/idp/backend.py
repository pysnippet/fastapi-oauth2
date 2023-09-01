from social_core.backends.oauth import BaseOAuth2


class TestOAuth2(BaseOAuth2):
    name = "test"
    AUTHORIZATION_URL = "http://idp/oauth/authorization"
    ACCESS_TOKEN_URL = "http://idp/oauth/token"
    ACCESS_TOKEN_METHOD = "POST"
    REDIRECT_STATE = False
    STATE_PARAMETER = True
    SEND_USER_AGENT = True
