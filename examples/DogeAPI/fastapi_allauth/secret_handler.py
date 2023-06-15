from typing import Union

from pydantic import SecretStr

SecretType = Union[str, SecretStr]


def _get_secret_value(secret: SecretStr):
    if isinstance(secret, SecretStr):
        return secret.get_secret_value()
    return secret
