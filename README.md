# fastapi-oauth2 <img src="https://github.com/pysnippet.png" align="right" height="64" />

[![PyPI](https://img.shields.io/pypi/v/fastapi-oauth2.svg)](https://pypi.org/project/fastapi-oauth2/)
[![Python](https://img.shields.io/pypi/pyversions/fastapi-oauth2.svg?logoColor=white)](https://pypi.org/project/fastapi-oauth2/)
[![FastAPI](https://img.shields.io/badge/fastapi-%E2%89%A50.68.1-009486)](https://pypi.org/project/fastapi-oauth2/)
[![Tests](https://github.com/pysnippet/fastapi-oauth2/actions/workflows/tests.yml/badge.svg)](https://github.com/pysnippet/fastapi-oauth2/actions/workflows/tests.yml)
[![Docs](https://github.com/pysnippet/fastapi-oauth2/actions/workflows/docs.yml/badge.svg)](https://github.com/pysnippet/fastapi-oauth2/actions/workflows/docs.yml)

FastAPI OAuth2 is a middleware-based social authentication mechanism supporting several OAuth2 providers. It leverages
the [social-core](https://github.com/python-social-auth/social-core) authentication backends and integrates seamlessly
with FastAPI applications.

## Integration

For integrating the package into an existing FastAPI application, the router with OAuth2 routes and
the `OAuth2Middleware` with particular [configs](https://docs.pysnippet.org/fastapi-oauth2/integration/configuration)
should be added to the application.

```python
from fastapi import FastAPI
from fastapi_oauth2.middleware import OAuth2Middleware
from fastapi_oauth2.router import router as oauth2_router

app = FastAPI()
app.include_router(oauth2_router)
app.add_middleware(OAuth2Middleware, config=OAuth2Config(...))
```

## Contribute

Any contribution is welcome. Always feel free to open an issue or a discussion if you have any questions not covered by
the documentation. If you have any ideas or suggestions, please, open a pull request. Your name will shine in our
contributors' list. Be proud of what you build!

## License

Copyright (C) 2023 Artyom Vancyan. [MIT](https://github.com/pysnippet/fastapi-oauth2/blob/master/LICENSE)
