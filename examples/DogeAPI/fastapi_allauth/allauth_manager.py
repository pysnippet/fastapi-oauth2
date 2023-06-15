from functools import wraps
from typing import Optional

from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session

from .auth import login, register, AuthHandler
from .model import BaseUser
from .oauth.BaseOauth import BaseOauth
from .secret_handler import SecretType


class AllauthManager:
    db: Session
    user: BaseUser
    secret: SecretType
    lifetime_second: int = 3600

    def __init__(self, db, user, secret, lifetime_second) -> None:
        self.db = db
        self.user = user
        self.secret = secret
        self.lifetime_second = lifetime_second

    def get_oauth_router(self, oauth: BaseOauth) -> APIRouter:

        router = APIRouter()

        @router.get("/authorize")
        async def authorize(scope: Optional[str] = None):
            url = await oauth.get_authorization_url(scope=scope)
            return {"url": url}

        @router.get("/callback")
        async def callback(code: Optional[str] = None, state: Optional[str] = None):
            tokens = await oauth.get_access_token(code=code, state=state)
            user_json = oauth.get_userinfo(tokens["access_token"])
            _user = self.user.create(
                open_id=oauth.get_open_id(user_json=user_json), provider=oauth.provider)

            if self.get_user_by_authority(_user.authority) is None:
                try:
                    register(self.db, _user)
                except Exception("Register failed"):
                    pass

            return login(_user, self.secret, self.lifetime_second)

        return router

    def get_user_by_authority(self, authority: str):
        return self.db.query(BaseUser).filter(BaseUser.authority == authority).first()

    def login_required(self, func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            auth_handler = AuthHandler(self.secret, self.lifetime_second)
            token = kwargs.get('authorization', False)
            if token:
                authority = auth_handler.decode_access_token(token)

                if not self.get_user_by_authority(authority):
                    raise HTTPException(status_code=401, detail="user not exist")

            else:
                raise HTTPException(status_code=401, detail="token required")

            # success
            return await func(*args, **kwargs)

        return wrapper
