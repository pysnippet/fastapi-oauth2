from fastapi import APIRouter
from fastapi import Request
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse

from fastapi_oauth2.security import OAuth2

oauth2 = OAuth2()
router_api = APIRouter()
templates = Jinja2Templates(directory="templates")


@router_api.get("/auth")
def sim_auth(request: Request):
    access_token = request.auth.jwt_create({
        "id": 1,
        "identity": "demo:1",
        "image": None,
        "display_name": "John Doe",
        "email": "john.doe@auth.sim",
        "username": "JohnDoe",
        "exp": 3689609839,
    })
    response = RedirectResponse("/")
    response.set_cookie(
        "Authorization",
        value=f"Bearer {access_token}",
        max_age=request.auth.expires,
        expires=request.auth.expires,
        httponly=request.auth.http,
    )
    return response
