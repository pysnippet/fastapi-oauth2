# fastapi-oauth2 <img src="https://github.com/pysnippet.png" align="right" height="64" />

[![PyPI](https://img.shields.io/pypi/v/fastapi-oauth2.svg)](https://pypi.org/project/fastapi-oauth2/)
[![Playground](https://img.shields.io/badge/playground-blue.svg?logo=data:image/svg+xml;base64,PD94bWwgdmVyc2lvbj0iMS4wIiBzdGFuZGFsb25lPSJubyI/PjwhRE9DVFlQRSBzdmcgUFVCTElDICItLy9XM0MvL0RURCBTVkcgMS4xLy9FTiIgImh0dHA6Ly93d3cudzMub3JnL0dyYXBoaWNzL1NWRy8xLjEvRFREL3N2ZzExLmR0ZCI+PHN2ZyB0PSIxNzEzNTE0OTc5MTUzIiBjbGFzcz0iaWNvbiIgdmlld0JveD0iMCAwIDEwMjQgMTAyNCIgdmVyc2lvbj0iMS4xIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHAtaWQ9IjE2MjciIHhtbG5zOnhsaW5rPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5L3hsaW5rIiB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCI+PHBhdGggZD0iTTc2OCA1MDYuMDI2NjY3djExLjk0NjY2NmEzMi40MjY2NjcgMzIuNDI2NjY3IDAgMCAxLTE1Ljc4NjY2NyAyNy43MzMzMzRMMzcwLjM0NjY2NyA3NjhjLTIzLjA0IDEzLjY1MzMzMy0zNC45ODY2NjcgMTMuNjUzMzMzLTQ1LjIyNjY2NyA3LjY4bC0xMC42NjY2NjctNS45NzMzMzNhMzIuNDI2NjY3IDMyLjQyNjY2NyAwIDAgMS0xNS43ODY2NjYtMjYuODhWMjgxLjE3MzMzM2EzMi40MjY2NjcgMzIuNDI2NjY3IDAgMCAxIDE1Ljc4NjY2Ni0yNy43MzMzMzNsMTAuNjY2NjY3LTUuOTczMzMzYzEwLjI0LTUuOTczMzMzIDIyLjE4NjY2Ny01Ljk3MzMzMyA1Mi4wNTMzMzMgMTEuNTJsMzc1LjA0IDIxOS4zMDY2NjZhMzIuNDI2NjY3IDMyLjQyNjY2NyAwIDAgMSAxNS43ODY2NjcgMjcuNzMzMzM0eiIgcC1pZD0iMTYyOCIgZGF0YS1zcG0tYW5jaG9yLWlkPSJhMzEzeC5zZWFyY2hfaW5kZXguMC5pMS40NzE5M2E4MVdiYjYyWiIgY2xhc3M9IiIgZmlsbD0iI2ZmZmZmZiI+PC9wYXRoPjwvc3ZnPg==)](https://playground.pysnippet.org/fastapi-oauth2/)
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
