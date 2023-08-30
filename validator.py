from oauthlib.oauth2 import Client
from oauthlib.oauth2 import RequestValidator


class MyRequestValidator(RequestValidator):

    def validate_client_id(self, client_id, request, *args, **kwargs):
        return True

    def validate_redirect_uri(self, client_id, redirect_uri, request, *args, **kwargs):
        return True

    def get_default_redirect_uri(self, client_id, request, *args, **kwargs):
        return ""

    def get_default_scopes(self, client_id, request, *args, **kwargs):
        return []

    def authenticate_client(self, request, *args, **kwargs):
        request.client = Client(client_id="my_client", access_token="my_token")
        return True

    def confirm_redirect_uri(self, client_id, code, redirect_uri, client, request, *args, **kwargs):
        return True

    def validate_code(self, client_id, code, client, request, *args, **kwargs):
        return True

    def validate_scopes(self, client_id, scopes, client, request, *args, **kwargs):
        return True

    def save_authorization_code(self, client_id, code, request, *args, **kwargs):
        return True

    def validate_response_type(self, client_id, response_type, client, request, *args, **kwargs):
        return True

    def validate_grant_type(self, client_id, grant_type, client, request, *args, **kwargs):
        return True

    def save_bearer_token(self, token, request, *args, **kwargs):
        return True

    def invalidate_authorization_code(self, client_id, code, request, *args, **kwargs):
        return True
