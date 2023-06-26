import json
import os

from dotenv import load_dotenv
from fastapi import FastAPI, Request, APIRouter
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from social_core.backends.github import GithubOAuth2

from demo.router import router as demo_router
from fastapi_oauth2.client import OAuth2Client
from fastapi_oauth2.middleware import OAuth2Middleware
from fastapi_oauth2.router import router as oauth2_router

load_dotenv()
router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "user": request.user, "json": json})


app = FastAPI()
app.include_router(router)
app.include_router(demo_router)
app.include_router(oauth2_router)
app.add_middleware(OAuth2Middleware, config={
    "allow_http": True,
    "jwt_secret": os.getenv("JWT_SECRET"),
    "jwt_expires": os.getenv("JWT_EXPIRES"),
    "jwt_algorithm": os.getenv("JWT_ALGORITHM"),
    "clients": [
        OAuth2Client(
            backend=GithubOAuth2,
            client_id=os.getenv("OAUTH2_CLIENT_ID"),
            client_secret=os.getenv("OAUTH2_CLIENT_SECRET"),
            # redirect_uri="http://127.0.0.1:8000/",
            scope=["user:email"],
        ),
    ]
})
