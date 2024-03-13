from urllib.parse import parse_qs
from urllib.parse import urlencode
from urllib.parse import urlparse

import pytest
from httpx import AsyncClient
from jose.jwt import encode as jwt_encode
from oauthlib.oauth2 import WebApplicationClient


async def oauth2_workflow(get_app, idp=False, ssr=True, authorize_query="", token_query="", use_header=False):
    async with AsyncClient(app=get_app(with_idp=idp, with_ssr=ssr), base_url="http://test") as client:
        response = await client.get("/user")
        assert response.status_code == 403  # Forbidden

        response = await client.get("/oauth2/test/authorize" + authorize_query)  # Get authorization endpoint
        authorization_endpoint = response.headers.get("location") if ssr else response.json().get("url")
        response = await client.get(authorization_endpoint)  # Authorize
        token_url = response.headers.get("location")
        query = {k: v[0] for k, v in parse_qs(urlparse(token_url).query).items()}
        query.update({k: v[0] for k, v in parse_qs(token_query).items()})
        token_url = "%s?%s" % (token_url.split("?")[0], urlencode(query))
        response = await client.get(token_url)  # Obtain token

        response = await client.get("/user", headers=dict(
            Authorization=jwt_encode(response.json(), "")  # Set token
        ) if use_header else None)
        assert response.status_code == 200  # OK


@pytest.mark.anyio
async def test_oauth2_basic_workflow(get_app):
    await oauth2_workflow(get_app, idp=True)
    await oauth2_workflow(get_app, idp=True, ssr=False, use_header=True)


@pytest.mark.anyio
async def test_oauth2_pkce_workflow(get_app):
    for code_challenge_method in (None, "S256"):
        # Generate the code verifier and challenge
        oauth_client = WebApplicationClient("test_id")
        code_verifier = oauth_client.create_code_verifier(128)
        code_challenge = oauth_client.create_code_challenge(code_verifier, code_challenge_method)

        aq = dict(code_challenge=code_challenge)
        if code_challenge_method:
            aq["code_challenge_method"] = code_challenge_method
        aq = "?" + urlencode(aq)
        tq = "&" + urlencode(dict(code_verifier=code_verifier))
        await oauth2_workflow(get_app, idp=True, authorize_query=aq, token_query=tq)
        await oauth2_workflow(get_app, idp=True, ssr=False, authorize_query=aq, token_query=tq, use_header=True)


@pytest.mark.anyio
async def test_oauth2_csrf_workflow(get_app):
    for aq, tq in [
        ("?state=test_state", "&state=test_state"),
        ("?state=test_state", "&state=test_wrong_state")
    ]:
        try:
            await oauth2_workflow(get_app, idp=True, authorize_query=aq, token_query=tq)
            await oauth2_workflow(get_app, idp=True, ssr=False, authorize_query=aq, token_query=tq, use_header=True)
        except AssertionError:
            assert aq != tq


@pytest.mark.anyio
async def test_core_access_token(get_app):
    async with AsyncClient(app=get_app(with_idp=True, with_ssr=True), base_url="http://test") as client:
        response = await client.get("/oauth2/test/authorize")
        authorization_endpoint = response.headers.get("location")
        response = await client.get(authorization_endpoint)
        token_url = response.headers.get("location")
        query = {k: v[0] for k, v in parse_qs(urlparse(token_url).query).items()}
        token_url = "%s?%s" % (token_url.split("?")[0], urlencode(query))
        await client.get(token_url)

        response = await client.get("/access-token")
        assert response.content != b""

        response = await client.get("/access-token")
        assert response.content != b""
