import os

from dotenv import load_dotenv

load_dotenv()

OAUTH2_CLIENT_ID = os.getenv("OAUTH2_CLIENT_ID")
OAUTH2_CLIENT_SECRET = os.getenv("OAUTH2_CLIENT_SECRET")
OAUTH2_CALLBACK_URL = os.getenv("OAUTH2_CALLBACK_URL")
OAUTH2_REDIRECT_URL = os.getenv("OAUTH2_REDIRECT_URL")

JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")
JWT_EXPIRES = int(os.getenv("JWT_EXPIRES", "15"))
