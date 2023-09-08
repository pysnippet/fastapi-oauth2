# Configuration

The configuration for the OAuth2 clients can be provided by using the [`OAuth2Config`](#oauth2config)
and [`OAuth2Client`](#oauth2client) classes. There is an alternate way to define the configuration by using the
Python's `dict` type with the same structure as these two classes.

## OAuth2Config

The `OAuth2Config` class is used to define the middleware configuration, and it has the following attributes:

- `enable_ssr` - Whether enable server-side rendering or not. Defaults to `True`.
- `allow_http` - Whether allow HTTP requests or not. Defaults to `False`.
- `jwt_secret` - Secret used to sign the JWT tokens. Defaults to an empty string.
- `jwt_expires` - JWT lifetime in seconds. Defaults to 900 (15 minutes).
- `jwt_algorithm` - The algorithm used to sign the JWT tokens. Defaults to `HS256`.
- `clients` - A list of [`OAuth2Client`](#oauth2client) instances. Defaults to an empty list.

```python
OAuth2Config(
    allow_http=True,
    jwt_secret=os.getenv("JWT_SECRET"),
    jwt_expires=os.getenv("JWT_EXPIRES"),
    jwt_algorithm=os.getenv("JWT_ALGORITHM"),
    clients=[
        OAuth2Client(...),
        OAuth2Client(...),
    ]
)
```

## OAuth2Client

The `OAuth2Client` class is used to define the configuration for a given OAuth2 client, and it has the following
attributes:

- `backend` - A backend class from the `social_core.backends` package.
- `client_id` - A string value of the generated client ID.
- `client_secret` - A string value of the generated client secret.
- `redirect_uri` - URL to redirect to after the authentication. Defaults to the base URL.
- `scope` - A list of the desired scopes. Defaults to an empty list.
- `claims` - An instance of [`Claims`](#claims) with the claim mapping definitions.

```python
OAuth2Client(
    backend=GithubOAuth2,
    client_id=os.getenv("OAUTH2_GITHUB_CLIENT_ID"),
    client_secret=os.getenv("OAUTH2_GITHUB_CLIENT_SECRET"),
    redirect_uri="https://example.com/dashboard",
    scope=["user:email"],
    claims=Claims(...),
)
```

## Claims

The `Claims` class is used to define the claim mapping for a given OAuth2 client, and it has `display_name`, `identity`,
`picture`, and `email` permanent attributes. It also accepts custom attributes if your case is special. Each attribute
can have a value of a string or a callable that receives the user data and returns a string.

```python
Claims(
    # Map the `picture` claim to the `avatar_url` key in the user data.
    picture="avatar_url",
    # Calculate the `identity` claim based on the user data.
    identity=lambda user: f"{user.provider}:{user.id}",
)
```

Check out the [tutorial](/references/tutorials#claims-mapping) on claims mapping for a clearer understanding.
