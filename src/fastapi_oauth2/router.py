from fastapi import APIRouter
from fastapi.responses import RedirectResponse
from starlette.requests import Request

router = APIRouter(prefix="/oauth2")


@router.get("/{provider}/auth")
async def login(request: Request, provider: str):
    return await request.auth.clients[provider].login_redirect(request)


@router.get("/{provider}/token")
async def token(request: Request, provider: str):
    return await request.auth.clients[provider].token_redirect(request)


@router.get("/logout")
def logout(request: Request):
    response = RedirectResponse(request.base_url)
    response.delete_cookie("Authorization")
    return response
