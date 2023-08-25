# Tutorials

This documentation section contains samples and tutorials on important topics of using the library. Look at
the [examples](https://github.com/pysnippet/fastapi-oauth2/tree/master/examples)
and [tests](https://github.com/pysnippet/fastapi-oauth2/tree/master/tests) directories of the repository for other
use-case implementations. Feel free to open an [issue](https://github.com/pysnippet/fastapi-oauth2/issues/new/choose) or
a [discussion](https://github.com/pysnippet/fastapi-oauth2/discussions/new/choose) if your question is not covered by
the documentation.

## User authentication

For the basic authentication, you must already have generated the client ID and secret to configure
your `OAuth2Middleware` with at least one client configuration.

1. Go to the developer console or settings of your OAuth2 identity provider and generate new client credentials.
2. Provide the [client configuration](/integration/configuration#oauth2client) with the obtained client ID and secret
   into the clients of the middleware's config.
3. Set the `redirect_uri` of your application that you have also configured in the IDP.
4. Add the middleware and include the router to your application as shown in the [integration](/integration/integration)
   section.
5. Open the `/oauth2/{provider}/auth` endpoint on your browser and test the authentication flow. Check out
   the [router](/integration/integration#router) for the `{provider}` variable.

Once the authentication is successful, the user will be redirected to the `redirect_uri` and the `request.user` will
contain the user information obtained from the IDP.

## User provisioning

## Claims mapping

## CSRF protection

## PKCE support
