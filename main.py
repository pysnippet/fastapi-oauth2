import json

from fastapi import FastAPI, Request, APIRouter
from fastapi.responses import HTMLResponse
from fastapi.security.utils import get_authorization_scheme_param
from fastapi.templating import Jinja2Templates
from starlette.authentication import AuthenticationBackend
from starlette.middleware.authentication import AuthenticationMiddleware

from demo.dependencies import get_current_user
from demo.router import router as demo_router
from fastapi_oauth2.router import router as oauth2_router

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "user": request.user, "json": json})


app = FastAPI()
app.include_router(router)
app.include_router(demo_router)
app.include_router(oauth2_router)


class BearerTokenAuthBackend(AuthenticationBackend):
    async def authenticate(self, request):
        authorization = request.cookies.get("Authorization")
        scheme, param = get_authorization_scheme_param(authorization)

        if not scheme or not param:
            return "", None

        return authorization, await get_current_user(param)


@app.on_event('startup')
async def startup():
    app.add_middleware(AuthenticationMiddleware, backend=BearerTokenAuthBackend())
