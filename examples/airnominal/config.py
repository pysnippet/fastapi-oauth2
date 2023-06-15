import os

from dotenv import load_dotenv

load_dotenv()

# config for github SSO
CLIENT_ID = os.getenv("AIRNOMINAL_GITHUB_CLIENT_ID")
CLIENT_SECRET = os.getenv("AIRNOMINAL_GITHUB_CLIENT_SECRET")
redirect_url = os.getenv("AIRNOMINAL_GITHUB_REDIRECT_URL")
redirect_url_main_page = os.getenv("AIRNMONIAL_MAIN_PAGE_REDIRECT_URL")

# config for jwt generation
SECRET_KEY = os.getenv("AIRNOMINAL_JWT_SECRET_KEY")
ALGORITHM = os.getenv("AIRNOMINAL_JWT_ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("AIRNOMINAL_JWT_TOKEN_EXPIRES"))

bucket = os.getenv("AIRNOMINAL_INFLUX_BUCKET")
org = os.getenv("AIRNOMINAL_INFLUX_ORG")
token = os.getenv("AIRNOMINAL_INFLUX_TOKEN")
influx_url = os.getenv("AIRNOMINAL_INFLUX_URL")

mongo_url = os.getenv("AIRNOMINAL_MONGO_URL")
port = int(os.getenv("AIRNOMINAL_MONGO_PORT") or "0")
username = os.getenv("AIRNOMINAL_MONGO_USERNAME")
password = os.getenv("AIRNOMINAL_MONGO_PASSWORD")

api_root_path = os.getenv("AIRNOMINAL_ROOT_PATH") or ""
