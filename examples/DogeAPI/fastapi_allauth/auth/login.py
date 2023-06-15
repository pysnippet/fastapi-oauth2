from ..auth.authenticate import AuthHandler
from ..model.BaseUser import BaseUser
from ..secret_handler import SecretType, _get_secret_value


def login(user: BaseUser, secret: SecretType, lifetime_seconds: int):
    authhandler = AuthHandler(_get_secret_value(secret), lifetime_seconds)

    _payload = {}
    for key in user.payload:
        _payload[key] = user[key]

    token = authhandler.encode_login_token(payload=_payload)

    return token
