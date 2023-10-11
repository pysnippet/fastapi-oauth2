---
outline: deep
---

# Tutorials

This documentation section covers samples and tutorials on important topics of using the library. Look at
the [examples](https://github.com/pysnippet/fastapi-oauth2/tree/master/examples)
and [tests](https://github.com/pysnippet/fastapi-oauth2/tree/master/tests) directories of the repository for other
use-case implementations. Feel free to open an [issue](https://github.com/pysnippet/fastapi-oauth2/issues/new/choose) or
a [discussion](https://github.com/pysnippet/fastapi-oauth2/discussions/new/choose) if your question is not covered by
the documentation.

## Authentication

By following the [integration](/integration/integration) docs, for the basic user authentication, you must already have
generated the client ID and secret to configure your `OAuth2Middleware` with at least one client configuration.

1. Go to the developer console or settings of your OAuth2 identity provider and generate new client credentials.
2. Provide the [client configuration](/integration/configuration#oauth2client) with the obtained client ID and secret
   into the clients of the middleware's config.
3. Set the `redirect_uri` of your application that you have also configured in the IDP.
4. Add the middleware and include the router to your application as shown in the [integration](/integration/integration)
   section.
5. Open the `/oauth2/{provider}/authorize` endpoint on your browser and test the authentication flow. Check out
   the [router](/integration/integration#router) for the `{provider}` variable.

Once the authentication is successful, the user will be redirected to the `redirect_uri` and the `request.user` will
contain the user information obtained from the IDP.

## Access token

When the user is authenticated, the `request.user` will contain the user information obtained from the IDP and
the `request.auth` will contain the authentication related information including the access token issued by the IDP. It
can be used to perform authorized requests to the IDP's API endpoints. Just make sure the token is issued with the
scopes required for the API endpoint.

::: details `request.auth.provider.access_token`

```mermaid
flowchart TB
    subgraph level2["request (Starlette's Request object)"]
        direction TB
        subgraph level1["auth (Starlette's extended Auth Credentials)"]
            direction TB
            subgraph level0["provider (OAuth2 provider with client's credentials)"]
                direction TB
                token["access_token (Access token for the specified scopes)"]
            end
        end
    end
    style level2 fill: #00948680, color: #f6f6f7, stroke: #3c3c43;
    style level1 fill: #2b75a080, color: #f6f6f7, stroke: #3c3c43;
    style level0 fill: #5c837480, color: #f6f6f7, stroke: #3c3c43;
    style token fill: #44506980, color: #f6f6f7, stroke: #3c3c43;
```

:::

## Claims mapping

The `Claims` class includes permanent attributes like `display_name`, `identity`, `picture`, and `email`. It also allows
for custom attributes. Each attribute can either be a string or a callable function that takes user data and returns a
string. Suppose the user data obtained from IDP looks like follows, and you need to map the corresponding attributes for
the user provisioning and other stuff.

```json
{
  "id": 54321,
  "sub": "1234567890",
  "name": "John Doe",
  "provider": "github",
  "emails": [
    "john.doe@test.py"
  ],
  "avatar_url": "https://example.com/john.doe.png"
}
```

It looks easy for the `picture` and `display_name` attributes, but how to map `email` from `emails` or create a
unique `identity` attribute. Well, that is where the callable functions come in handy. You can use the `lambda` function
to map the attributes as follows.

```python
Claims(
    picture="image",
    display_name="avatar_url",
    email=lambda u: u.emails[0],
    identity=lambda u: f"{u.provider}:{u.sub}",
)
```

Not all IDPs provide the `first_name` and the `last_name` attributes already joined as in the example above, or
the email in a list. So you are given the flexibility using transformer function to map the attributes as you want.

```mermaid
flowchart LR
    IDPUserData("display_name string")
    FastAPIUserData("first_name string\nlast_name string")
    Transform[["transform into desired format"]]
    FastAPIUserData --> Transform
    Transform --> IDPUserData
```

## User provisioning

User provisioning refers to the process of creating, updating, and deleting user accounts within the OAuth2 IDP and
synchronizing that information with your FastAPI application's database. There are two approaches to user provisioning
and both require the user claims to be mapped properly for creating a new user or updating an existing one.

::: info NOTE

In both scenarios, it is recommended to use the `identity` attribute for uniquely identifying the user from the
database. So if the application uses or plans to use multiple IDPs, make sure to include the `provider` attribute when
calculating the `identity` attribute.

:::

### Automatic provisioning

After successful authentication, you can automatically create a user in your application's database using the
information obtained from the IDP. The user creation or update can be handled at the `callback` function of the
[middleware](/integration/integration#oauth2middleware) as it is called when authentication succeeds.

### Manual provisioning

After successful authentication, redirect the user to a registration form where they can complete their profile. This
approach is useful when there missing mandatory attributes in `request.user` for creating a user in your application's
database. You need to define a route for provisioning and provide it as `redirect_uri`, so
the [user context](/integration/integration#user-context) will be available for usage.

## Error handling

The exceptions that possibly can occur when using the library are reraised as `HTTPException` with the appropriate
status code and a message describing the actual error cause. So they can be handled in a natural way by following the
FastAPI [docs](https://fastapi.tiangolo.com/tutorial/handling-errors/) on handling errors and using the exceptions from
the `fastapi_oauth2.exceptions` module.

```python
from fastapi_oauth2.exceptions import OAuth2AuthenticationError

@app.exception_handler(OAuth2AuthenticationError)
async def error_handler(request: Request, exc: OAuth2AuthenticationError):
    return RedirectResponse(url="/login", status_code=303)
```

The complete list of exceptions is the following.

- `OAuth2Error` - Base exception for all errors raised by the FastAPI OAuth2 library.
- `OAuth2AuthenticationError` - An exception is raised when the authentication fails.
- `OAuth2InvalidRequestError` - An exception is raised when the request is invalid.

The request is considered invalid when one of mandatory parameters such as `state` or `code` is missing or the request
did not succeed.

<style>
.info, .details {
  border: 0;
}
</style>
