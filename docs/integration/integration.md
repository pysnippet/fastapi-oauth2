---
outline: deep
---

# Integration

In the previous section, were described the configuration components of the OAuth2 authentication middleware and this
section covers its integration into a FastAPI app.

## OAuth2Middleware

The `OAuth2Middleware` is an authentication middleware which means that its usage makes the `user` and `auth` attributes
available in the [request](https://www.starlette.io/requests/) context. It has a mandatory argument `config` of
[`OAuth2Config`](/integration/configuration#oauth2config) instance that has been discussed at the previous section and
an optional argument `callback` which is a callable that is called when the authentication succeeds.

```python
app: FastAPI

def on_auth_success(auth: Auth, user: User):
    """This could be async function as well."""

app.add_middleware(
    OAuth2Middleware,
    config=OAuth2Config(...),
    callback=on_auth_success,
)
```

### Auth context

This is extended version of Starlette's [`AuthCredentials`](https://www.starlette.io/authentication/#authcredentials)
and the difference is that the `Auth` has additionally the list of the `clients` that can be used in the Jinja templates
to display them dynamically, and the `provider` is an item of the `clients` that was used to authenticate the current
user. Also, there are some methods for managing the JWT tokens: `jwt_encode`, `jwt_decode`, and `jwt_create`.

### User context

This is the extended version of Starlette's [`BaseUser`](https://www.starlette.io/authentication/#users) and apart from
the default `is_authenticated` and `display_name` and the extended `identity`, `picture`, and `email` properties, it
also contains all attributes of the user received from a certain provider.

### Callback

The `callback` is called with the [`Auth`](#auth-context) and [`User`](#user-context) arguments when the authentication
succeeds. This can be used for migrating an external user into the system of the existing application. Apart from other
OAuth2 solutions that force using their base user models, certain architectural designs, or a database from a limited
set of choices, this kind of solution gives developers freedom.

## Router

Router defines the endpoints that are used for the authentication and logout. The authentication is done by
the `/oauth2/{provider}/auth` endpoint and the logout is done by the `/oauth2/logout` endpoint. The `{provider}` is the
name of the provider that is going to be used for the authentication and coincides with the `name` attribute of
the `backend` provided to the certain `OAuth2Client`.

```python
from fastapi_oauth2.router import router as oauth2_router

app.include_router(oauth2_router)
```

## Security

FastAPI's `OAuth2`, `OAuth2PasswordBearer` and `OAuth2AuthorizationCodeBearer` security models are supported, but in
case your application uses cookies for storing the authentication tokens, you can use the same named security models
from the `fastapi_oauth2.security` module.
