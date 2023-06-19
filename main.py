import json

import jwt
from fastapi import FastAPI, Request, APIRouter
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.authentication import AuthenticationBackend
from starlette.middleware.authentication import AuthenticationMiddleware

from demo.config import SECRET_KEY, ALGORITHM
from demo.router import router as auth_router

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "user": request.user, "json": json})


app = FastAPI()
app.include_router(router)
app.include_router(auth_router)


class BearerTokenAuthBackend(AuthenticationBackend):
    async def authenticate(self, request):
        authorization = request.cookies.get("Authorization")

        if not authorization:
            return "", None

        access_token = authorization.split(" ")[1]
        user = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])

        return authorization, user


@app.on_event('startup')
async def startup():
    app.add_middleware(AuthenticationMiddleware, backend=BearerTokenAuthBackend())
