# fastapi-oauth2

Easy to setup OAuth2 social authentication mechanism with support for several auth providers.

## Features

- Integrate with any existing FastAPI project (no dependencies of the project should stop the work of
  the `fastapi-oauth2`)
    * Implementation must allow to provide a context for configurations (also, see how it is done in another projects)
- Use multiple OAuth2 providers at the same time
    * There need to be provided a way to configure the OAuth2 for multiple providers
- Token -> user data, user data -> token easy conversion
- Customize OAuth2 routes
