import importlib
import os

import pytest
import social_core.backends as backends
from fastapi import APIRouter
from fastapi import Depends
from fastapi import FastAPI
from fastapi import Request
from social_core.backends.github import GithubOAuth2
from social_core.backends.oauth import BaseOAuth2
from starlette.responses import Response

from fastapi_oauth2.client import OAuth2Client
from fastapi_oauth2.middleware import OAuth2Middleware
from fastapi_oauth2.router import router as oauth2_router
from fastapi_oauth2.security import OAuth2

package_path = backends.__path__[0]


@pytest.fixture
def backends():
    backend_instances = []
    for module in os.listdir(package_path):
        try:
            module_instance = importlib.import_module("social_core.backends.%s" % module[:-3])
            backend_instances.extend([
                attr for attr in module_instance.__dict__.values()
                if type(attr) is type and all([
                    issubclass(attr, BaseOAuth2),
                    attr is not BaseOAuth2,
                ])
            ])
        except ImportError:
            continue
    return backend_instances


@pytest.fixture
def app():
    oauth2 = OAuth2()
    application = FastAPI()
    app_router = APIRouter()

    @app_router.get("/user")
    def user(request: Request, _: str = Depends(oauth2)):
        return request.user

    @app_router.get("/auth")
    def auth(request: Request):
        access_token = request.auth.jwt_create({
            "name": "test",
            "sub": "test",
            "id": "test",
        })
        response = Response()
        response.set_cookie(
            "Authorization",
            value=f"Bearer {access_token}",
            max_age=request.auth.expires,
            expires=request.auth.expires,
            httponly=request.auth.http,
        )
        return response

    application.include_router(app_router)
    application.include_router(oauth2_router)
    application.add_middleware(OAuth2Middleware, config={
        "allow_http": True,
        "clients": [
            OAuth2Client(
                backend=GithubOAuth2,
                client_id="test_id",
                client_secret="test_secret",
            ),
        ],
    })

    return application
