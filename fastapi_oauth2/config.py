import os

from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
CALLBACK_URL = os.getenv("CALLBACK_URL")
REDIRECT_URL = os.getenv("REDIRECT_URL")

JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")
JWT_EXPIRES = int(os.getenv("JWT_EXPIRES"))
