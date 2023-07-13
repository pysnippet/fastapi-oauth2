import json

from fastapi import Depends
from fastapi import Request, APIRouter
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2
from fastapi.templating import Jinja2Templates

oauth2 = OAuth2()
router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "user": request.user, "json": json})


@router.get("/user")
def user(request: Request, _: str = Depends(oauth2)):
    return request.user
