import json

from fastapi import APIRouter
from fastapi import Depends
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from database import get_db
from fastapi_oauth2.security import OAuth2
from models import User

oauth2 = OAuth2()
router_ssr = APIRouter()
templates = Jinja2Templates(directory="templates")


@router_ssr.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {
        "json": json,
        "request": request,
    })


@router_ssr.get("/users", response_class=HTMLResponse)
async def users(request: Request, db: Session = Depends(get_db), _: str = Depends(oauth2)):
    return templates.TemplateResponse("users.html", {
        "json": json,
        "request": request,
        "users": [
            dict([(k, v) for k, v in user.__dict__.items() if not k.startswith("_")]) for user in db.query(User).all()
        ],
    })
