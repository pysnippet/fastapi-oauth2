import os

from dotenv import load_dotenv

load_dotenv()

# config for GitHub SSO
CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")
redirect_url = os.getenv("GITHUB_REDIRECT_URL")
redirect_url_main_page = os.getenv("MAIN_PAGE_REDIRECT_URL")

# config for jwt generation
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = os.getenv("JWT_ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_TOKEN_EXPIRES"))
