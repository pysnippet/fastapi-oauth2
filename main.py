import json

from fastapi import FastAPI, Request, APIRouter
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from social_core.backends.github import GithubOAuth2

from demo.router import router as demo_router
from fastapi_oauth2.middleware import OAuth2Middleware
from fastapi_oauth2.router import router as oauth2_router
from fastapi_oauth2.types import OAuth2Client

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
    "clients": [
        OAuth2Client(
            backend=GithubOAuth2,
            client_id="eccd08d6736b7999a32a",
            client_secret="642999c1c5f2b3df8b877afdc78252ef5b594d31",
            redirect_uri="http://127.0.0.1:8000/",
        ),
    ]
})
