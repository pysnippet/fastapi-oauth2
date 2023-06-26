from fastapi import APIRouter
from fastapi import Depends
from starlette.requests import Request

from .dependencies import oauth2_scheme

router = APIRouter()


@router.get("/user")
def user(request: Request, _: str = Depends(oauth2_scheme)):
    return request.user


@router.post("/token")
def token(request: Request):
    return request.cookies.get("Authorization")
