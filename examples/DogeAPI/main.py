#!/usr/bin/python3

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.responses import HTMLResponse

from core import auth, blog, user
from database.configuration import engine, get_db
from fastapi_allauth import AllauthManager
from fastapi_allauth.oauth import GithubOauth
from models import models
from models.models import User

models.Base.metadata.create_all(bind=engine)

allauthManager = AllauthManager(db=next(get_db()), user=User, secret="secret", lifetime_second=3600)
githubOauth = GithubOauth(
    client_id="eccd08d6736b7999a32a",
    client_secret="642999c1c5f2b3df8b877afdc78252ef5b594d31",
    redirect_uri="http://127.0.0.1:8000/github/callback",
    scope=["openid", "profile"]
)

app = FastAPI(
    title="DogeAPI",
    description="API with high performance built with FastAPI & SQLAlchemy, help to improve connection with your Backend Side.",
    version="1.0.0",
)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

app.include_router(auth.router)
app.include_router(blog.router)
app.include_router(user.router)
app.include_router(allauthManager.get_oauth_router(githubOauth), prefix="/github", tags=["github"])


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """
    Home page

    Args:
        request (Request): Request object

    Returns:
        HTMLResponse: HTML response
    """
    return templates.TemplateResponse("index.html", {"request": request})
