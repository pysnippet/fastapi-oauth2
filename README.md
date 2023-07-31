# fastapi-oauth2 <img src="https://github.com/pysnippet.png" align="right" height="64" />

[![PyPI](https://img.shields.io/pypi/v/fastapi-oauth2.svg)](https://pypi.org/project/fastapi-oauth2/)
[![Python](https://img.shields.io/pypi/pyversions/fastapi-oauth2.svg?logoColor=white)](https://pypi.org/project/fastapi-oauth2/)
[![FastAPI](https://img.shields.io/badge/fastapi-%E2%89%A50.68.1-009486)](https://pypi.org/project/fastapi-oauth2/)
[![Tests](https://github.com/pysnippet/fastapi-oauth2/actions/workflows/tests.yml/badge.svg)](https://github.com/pysnippet/fastapi-oauth2/actions/workflows/tests.yml)
[![License](https://img.shields.io/pypi/l/fastapi-oauth2.svg)](https://github.com/pysnippet/fastapi-oauth2/blob/master/LICENSE)

FastAPI OAuth2 is a middleware-based social authentication mechanism supporting several auth providers. It depends on
the [social-core](https://github.com/python-social-auth/social-core) authentication backends.

## Features to be implemented

- Use multiple OAuth2 providers at the same time
    * There need to be provided a way to configure the OAuth2 for multiple providers
- Customizable OAuth2 routes

## Installation

```shell
python -m pip install fastapi-oauth2
```

## Configuration

Configuration requires you to provide the JWT requisites and define the clients of the particular providers. The
middleware configuration is declared with the `OAuth2Config` and `OAuth2Client` classes.

### OAuth2Config

- `allow_http` - Allow insecure HTTP requests. Defaults to `False`.
- `jwt_secret` - The secret key used to sign the JWT. Defaults to `None`.
- `jwt_expires` - The expiration time of the JWT in seconds. Defaults to `900`.
- `jwt_algorithm` - The algorithm used to sign the JWT. Defaults to `HS256`.
- `clients` - The list of the OAuth2 clients. Defaults to `[]`.

### OAuth2Client

- `backend` - The [social-core](https://github.com/python-social-auth/social-core) authentication backend classname.
- `client_id` - The OAuth2 client ID for the particular provider.
- `client_secret` - The OAuth2 client secret for the particular provider.
- `redirect_uri` - The OAuth2 redirect URI to redirect to after success. Defaults to the base URL.
- `scope` - The OAuth2 scope for the particular provider. Defaults to `[]`.
- `claims` - Claims mapping for the certain provider.

It is also important to mention that for the configured clients of the auth providers, the authorization URLs are
accessible by the `/oauth2/{provider}/auth` path where the `provider` variable represents the exact value of the auth
provider backend `name` attribute.

```python
from fastapi_oauth2.claims import Claims
from fastapi_oauth2.client import OAuth2Client
from fastapi_oauth2.config import OAuth2Config
from social_core.backends.github import GithubOAuth2

oauth2_config = OAuth2Config(
    allow_http=False,
    jwt_secret=os.getenv("JWT_SECRET"),
    jwt_expires=os.getenv("JWT_EXPIRES"),
    jwt_algorithm=os.getenv("JWT_ALGORITHM"),
    clients=[
        OAuth2Client(
            backend=GithubOAuth2,
            client_id=os.getenv("OAUTH2_CLIENT_ID"),
            client_secret=os.getenv("OAUTH2_CLIENT_SECRET"),
            redirect_uri="https://pysnippet.org/",
            scope=["user:email"],
            claims=Claims(
                picture="avatar_url",
                identity=lambda user: "%s:%s" % (user.get("provider"), user.get("id")),
            ),
        ),
    ]
)
```

## Integration

To integrate the package into your FastAPI application, you need to add the `OAuth2Middleware` with particular configs
in the above-represented format and include the router to the main router of the application.

```python
from fastapi import FastAPI
from fastapi_oauth2.middleware import OAuth2Middleware
from fastapi_oauth2.router import router as oauth2_router

app = FastAPI()
app.include_router(oauth2_router)
app.add_middleware(OAuth2Middleware, config=oauth2_config)
```

After adding the middleware, the `user` attribute will be available in the request context. It will contain the user
data provided by the OAuth2 provider.

```jinja2
{% if request.user.is_authenticated %}
    <a href="/oauth2/logout">Sign out</a>
{% else %}
    <a href="/oauth2/github/auth">Sign in</a>
{% endif %}
```

## Contribute

Any contribution is welcome. If you have any ideas or suggestions, feel free to open an issue or a pull request. And
don't forget to add tests for your changes.

## License

Copyright (C) 2023 Artyom Vancyan. [MIT](https://github.com/pysnippet/fastapi-oauth2/blob/master/LICENSE)
