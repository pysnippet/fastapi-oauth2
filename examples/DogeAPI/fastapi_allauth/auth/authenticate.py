import time
from datetime import datetime, timedelta

import jwt
from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from ..secret_handler import SecretType, _get_secret_value

INVALID = "Invalid token"


class AuthHandler:
    secret: SecretType
    lifetime: int

    def __init__(self, secret, lifetime_seconds) -> None:
        self.secret = secret
        self.lifetime_seconds = lifetime_seconds

    security = HTTPBearer()

    @staticmethod
    def datetime_from_utc_to_local(utc_datetime):
        epoch = time.mktime(utc_datetime.timetuple())
        offset = datetime.fromtimestamp(
            epoch) - datetime.utcfromtimestamp(epoch)
        return utc_datetime + offset

    def encode_token(self, payload: dict, type):
        payload['sub'] = type
        local_datetime = self.datetime_from_utc_to_local(datetime.utcnow())
        if type == "access_token":
            payload.update(
                {"exp": local_datetime + timedelta(seconds=self.lifetime_seconds)})
        else:
            payload.update({"exp": local_datetime + timedelta(hours=720)})

        return jwt.encode(payload, _get_secret_value(self.secret), algorithm='HS256')

    def encode_login_token(self, payload: dict):
        access_token = self.encode_token(payload, "access_token")
        refresh_token = self.encode_token(payload, "refresh_token")

        login_token = dict(
            access_token=f"{access_token}",
            refresh_token=f"{refresh_token}"
        )
        return login_token

    def encode_update_token(self, payload: dict):
        access_token = self.encode_token(payload, "access_token")

        update_token = dict(
            access_token=f"{access_token}"
        )
        return update_token

    def decode_access_token(self, token):

        try:
            payload = jwt.decode(token, _get_secret_value(self.secret), algorithms=['HS256'])
            if payload['sub'] != "access_token":
                raise HTTPException(status_code=401, detail=INVALID)
            return payload['authority']
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=401, detail='Signature has expired')
        except jwt.InvalidTokenError as e:
            raise HTTPException(status_code=401, detail=INVALID)

    def decode_refresh_token(self, token):
        try:
            payload = jwt.decode(token, _get_secret_value(self.secret), algorithms=['HS256'])
            if payload['sub'] != "refresh_token":
                raise HTTPException(status_code=401, detail=INVALID)
            return payload['authority']
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=401, detail='Signature has expired')
        except jwt.InvalidTokenError as e:
            raise HTTPException(status_code=401, detail=INVALID)

    def auth_access_wrapper(self, auth: HTTPAuthorizationCredentials = Security(security)):
        return self.decode_access_token(auth.credentials)

    def auth_refresh_wrapper(self, auth: HTTPAuthorizationCredentials = Security(security)):
        return self.decode_refresh_token(auth.credentials)
