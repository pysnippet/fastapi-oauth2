# fastapi-oauth2 <img src="https://github.com/pysnippet.png" align="right" height="64" />

[//]: # (TODO: LONG DESCRIPTION)

## Features to be implemented

- Use multiple OAuth2 providers at the same time
    * There need to be provided a way to configure the OAuth2 for multiple providers
- Token -> user data, user data -> token easy conversion
- Customize OAuth2 routes

## Installation

```shell
python -m pip install fastapi-oauth2
```

## Configuration

[//]: # (TODO: LONG DESCRIPTION)

```python
from fastapi_oauth2.client import OAuth2Client
from fastapi_oauth2.config import OAuth2Config
from social_core.backends.github import GithubOAuth2

oauth2_config = OAuth2Config(
    allow_http=True,
    jwt_secret=os.getenv("JWT_SECRET"),
    jwt_expires=os.getenv("JWT_EXPIRES"),
    jwt_algorithm=os.getenv("JWT_ALGORITHM"),
    clients=[
        OAuth2Client(
            backend=GithubOAuth2,
            client_id=os.getenv("OAUTH2_CLIENT_ID"),
            client_secret=os.getenv("OAUTH2_CLIENT_SECRET"),
            scope=["user:email"],
        ),
    ]
)
```

## Usage

[//]: # (TODO: LONG DESCRIPTION)

```python
from fastapi import FastAPI
from fastapi_oauth2.middleware import OAuth2Middleware

app = FastAPI()
app.add_middleware(OAuth2Middleware, config=oauth2_config)
```

[//]: # (TODO: LONG DESCRIPTION)

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
