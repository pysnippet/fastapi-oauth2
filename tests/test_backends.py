import os
import pytest

from fastapi_oauth2.client import OAuth2Client
from fastapi_oauth2.core import OAuth2Core


@pytest.mark.anyio
async def test_core_init_with_all_backends(backends):
    
    # azuread-b2c-oauth2
    os.environ['SOCIAL_AUTH_AZUREAD_B2C_OAUTH2_TENANT_NAME'] = 'test'
    os.environ['SOCIAL_AUTH_AZUREAD_B2C_OAUTH2_POLICY'] = 'b2c_test'
    # UFFD backend
    os.environ['SOCIAL_AUTH_UFFD_BASE_URL'] = 'test'
    # OIDC backend (OpenID Connect)
    os.environ['SOCIAL_AUTH_OIDC_ENDPOINT'] = 'https://oidctest.wsweet.org'

    for backend in backends:
        try:
            # Vend backend 
            if backend.__name__ == 'VendOAuth2': 
                continue # malformed backend
            
            OAuth2Core(OAuth2Client(
                backend=backend,
                client_id="test_client_id",
                client_secret="test_client_secret",
            ))
        except (NotImplementedError, Exception):
            assert False
