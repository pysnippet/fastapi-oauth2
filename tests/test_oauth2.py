import time
from urllib.parse import parse_qs
from urllib.parse import urlencode
from urllib.parse import urlparse

import pytest
from httpx import AsyncClient
from jose.jwt import encode as jwt_encode
from oauthlib.oauth2 import WebApplicationClient

from fastapi_oauth2.config import OAuth2Config
from fastapi_oauth2.csrf_state import CookieStateBackend
from fastapi_oauth2.csrf_state import InMemoryStateBackend
from tests.conftest import TEST_JWT_SECRET


async def oauth2_workflow(get_app, idp=False, ssr=True, authorize_query="", token_query="", use_header=False):
    async with AsyncClient(app=get_app(with_idp=idp, with_ssr=ssr), base_url="http://test") as client:
        response = await client.get("/user")
        assert response.status_code in (401, 403)  # Unauthorized or Forbidden

        response = await client.get("/oauth2/test/authorize" + authorize_query)  # Get authorization endpoint
        authorization_endpoint = response.headers.get("location") if ssr else response.json().get("url")
        response = await client.get(authorization_endpoint)  # Authorize
        token_url = response.headers.get("location")
        query = {k: v[0] for k, v in parse_qs(urlparse(token_url).query).items()}
        query.update({k: v[0] for k, v in parse_qs(token_query).items()})
        token_url = "%s?%s" % (token_url.split("?")[0], urlencode(query))
        response = await client.get(token_url)  # Obtain token

        response = await client.get("/user", headers=dict(
            Authorization="Bearer " + jwt_encode({**response.json(), "exp": int(time.time()) + 60}, TEST_JWT_SECRET)
        ) if use_header else None)
        assert response.status_code == 200  # OK
        assert response.json().get("provider") == "test"  # Authenticated from the verified token


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


@pytest.mark.anyio
async def test_oauth2_cookie_state_backend_workflow(get_app):
    async with AsyncClient(app=get_app(with_idp=True, with_ssr=True, state_backend=CookieStateBackend()), base_url="http://test") as client:
        response = await client.get("/oauth2/test/authorize")
        assert response.status_code == 303  # Redirect
        assert "CSRFState=" in response.headers.get("set-cookie", "")  # State cookie issued
        authorization_endpoint = response.headers.get("location")
        response = await client.get(authorization_endpoint)
        token_url = response.headers.get("location")
        query = {k: v[0] for k, v in parse_qs(urlparse(token_url).query).items()}
        token_url = "%s?%s" % (token_url.split("?")[0], urlencode(query))
        response = await client.get(token_url)
        assert response.status_code == 307  # Redirect

        response = await client.get("/user")
        assert response.status_code == 200  # OK


@pytest.mark.anyio
async def test_oauth2_cookie_state_rejects_mismatch(get_app):
    async with AsyncClient(app=get_app(with_idp=True, with_ssr=True, state_backend=CookieStateBackend()), base_url="http://test") as client:
        await client.get("/oauth2/test/authorize")  # Issue the signed state cookie
        response = await client.get("/oauth2/test/token?state=forged&code=whatever")
        assert response.status_code == 400  # Bad Request


async def capture_callback_url(client):
    response = await client.get("/oauth2/test/authorize")
    response = await client.get(response.headers["location"])  # IdP issues a real code + state
    return response.headers["location"]


@pytest.mark.anyio
@pytest.mark.parametrize("state_backend", [None, InMemoryStateBackend, CookieStateBackend])
async def test_oauth2_callback_not_replayable_by_other_browser(get_app, state_backend):
    # GHSA-wqf2-2c92-hpvj: a callback URL captured by the attacker must not log the victim in
    app = get_app(with_idp=True, with_ssr=True, state_backend=state_backend and state_backend())

    async with AsyncClient(app=app, base_url="http://test") as attacker:
        callback_url = await capture_callback_url(attacker)

    async with AsyncClient(app=app, base_url="http://test") as victim:
        response = await victim.get(callback_url)
        assert response.status_code == 400  # Bad Request
        assert "Authorization" not in response.headers.get("set-cookie", "")

        response = await victim.get("/user")
        assert response.status_code in (401, 403)  # Still unauthenticated


@pytest.mark.anyio
async def test_oauth2_in_memory_state_concurrent_flows(get_app):
    app = get_app(with_idp=True, with_ssr=True, state_backend=InMemoryStateBackend())
    async with AsyncClient(app=app, base_url="http://test") as client:
        first = await capture_callback_url(client)  # e.g. two tabs of the same browser
        second = await capture_callback_url(client)

        assert (await client.get(first)).status_code == 307
        assert (await client.get(second)).status_code == 307
        assert (await client.get("/user")).status_code == 200


def test_default_state_backend_depends_on_ssr():
    assert isinstance(OAuth2Config(jwt_secret=TEST_JWT_SECRET).state_backend, CookieStateBackend)
    assert OAuth2Config(jwt_secret=TEST_JWT_SECRET, enable_ssr=False).state_backend is None  # in-memory fallback


@pytest.mark.anyio
@pytest.mark.parametrize("state_backend", [None, InMemoryStateBackend, CookieStateBackend])
async def test_oauth2_state_cookie_survives_strict_same_site(get_app, state_backend):
    # A SameSite=Strict state cookie would not be sent on the cross-site redirect back from the IdP
    app = get_app(with_idp=True, with_ssr=True, same_site="strict", state_backend=state_backend and state_backend())
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/oauth2/test/authorize")
        set_cookie = response.headers.get("set-cookie", "").lower()
        assert "samesite=lax" in set_cookie
        assert "samesite=strict" not in set_cookie

        response = await client.get(response.headers["location"])
        assert (await client.get(response.headers["location"])).status_code == 307
        assert (await client.get("/user")).status_code == 200
