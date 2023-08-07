import pytest

from fastapi_oauth2.client import OAuth2Client
from fastapi_oauth2.core import OAuth2Core


@pytest.mark.anyio
async def test_core_init_with_all_backends(backends):
    for backend in backends:
        try:
            OAuth2Core(OAuth2Client(
                backend=backend,
                client_id="test_client_id",
                client_secret="test_client_secret",
            ))
        except (NotImplementedError, Exception):
            assert False
