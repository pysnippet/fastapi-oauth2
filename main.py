import urllib.parse

from flask import Flask, request, jsonify, url_for, redirect
from oauthlib.oauth2 import Server

from validator import MyRequestValidator

app = Flask(__name__)

oauth2_server = Server(MyRequestValidator())


@app.route('/auth', methods=['GET', 'POST'])
def auth():
    if request.method == 'GET':
        try:
            # Validate the client request for authorization
            uri = request.url
            http_method = request.method
            headers = request.headers
            body = request.get_data()

            scopes, credentials = oauth2_server.validate_authorization_request(uri, http_method, body, headers)
            del credentials['request']
            action = url_for('auth') + "?" + urllib.parse.urlencode({"scopes": ','.join(scopes), **credentials})

            # Assuming the user is authenticated and named 'user1'
            # You can integrate real user authentication here
            return f"""
            Do you authorize the app to access your data?
            <form action="{action}" method="POST">
                <button type="submit">Yes</button>
            </form>
            """
        except:
            return "Invalid authorization request", 400

    elif request.method == 'POST':
        uri = request.url
        http_method = request.method
        headers = request.headers
        body = request.get_data()

        headers, body, status = oauth2_server.create_authorization_response(uri, http_method, body, headers)

        if status == 302:
            location = headers.get('Location', '')
            return redirect(location)

        return jsonify(body), status


@app.route('/token', methods=['POST'])
def token():
    uri = request.url
    http_method = request.method
    headers = request.headers
    body = request.get_data()

    headers, body, status = oauth2_server.create_token_response(uri, http_method, body, headers, {})

    return body, status


if __name__ == "__main__":
    app.run()
