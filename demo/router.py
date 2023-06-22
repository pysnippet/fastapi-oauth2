from fastapi import APIRouter
from fastapi import Depends
from starlette.requests import Request

from .dependencies import get_current_user

router = APIRouter()


@router.get("/user")
def user(current_user=Depends(get_current_user)):
    return current_user


@router.post("/token")
def token(request: Request):
    return request.cookies.get("Authorization")
