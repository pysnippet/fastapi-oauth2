import json

from fastapi import Depends
from fastapi import Request
from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from fastapi_oauth2.security import OAuth2

oauth2 = OAuth2()
router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "user": request.user, "json": json})


@router.get("/user")
def user(request: Request, _: str = Depends(oauth2)):
    return request.user
