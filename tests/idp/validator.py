import base64
import hashlib

from oauthlib.oauth2 import Client
from oauthlib.oauth2 import RequestValidator


class TestValidator(RequestValidator):
    pkce_codes = {}

    def validate_client_id(self, client_id, request, *args, **kwargs):
        return True

    def validate_redirect_uri(self, client_id, redirect_uri, request, *args, **kwargs):
        return True

    def get_default_redirect_uri(self, client_id, request, *args, **kwargs):
        return ""

    def get_default_scopes(self, client_id, request, *args, **kwargs):
        return []

    def authenticate_client(self, request, *args, **kwargs):
        request.client = Client(client_id="")
        return True

    def confirm_redirect_uri(self, client_id, code, redirect_uri, client, request, *args, **kwargs):
        return True

    def validate_code(self, client_id, code, client, request, *args, **kwargs):
        stored_challenge = self.pkce_codes.get(code)
        if not stored_challenge:
            return False

        code_verifier = request.code_verifier
        code_challenge = stored_challenge.get("code_challenge")
        code_challenge_method = stored_challenge.get("code_challenge_method")

        computed_challenge = code_verifier
        if code_challenge_method == "S256":
            sha256 = hashlib.sha256()
            sha256.update(code_verifier.encode("utf-8"))
            computed_challenge = base64.urlsafe_b64encode(sha256.digest()).decode("utf-8").replace("=", "")

        return computed_challenge == code_challenge

    def validate_scopes(self, client_id, scopes, client, request, *args, **kwargs):
        return True

    def save_authorization_code(self, client_id, code, request, *args, **kwargs):
        self.pkce_codes[code.get("code")] = dict(
            code_challenge=request.code_challenge,
            code_challenge_method=request.code_challenge_method,
        )
        return True

    def validate_response_type(self, client_id, response_type, client, request, *args, **kwargs):
        return True

    def validate_grant_type(self, client_id, grant_type, client, request, *args, **kwargs):
        return True

    def save_bearer_token(self, token, request, *args, **kwargs):
        return True

    def invalidate_authorization_code(self, client_id, code, request, *args, **kwargs):
        return True
