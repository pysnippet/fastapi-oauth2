from fastapi import APIRouter
from fastapi import FastAPI

from config import oauth2_config
from fastapi_oauth2.middleware import OAuth2Middleware
from fastapi_oauth2.router import router as oauth2_router
from router import router as app_router

router = APIRouter()

app = FastAPI()
app.include_router(app_router)
app.include_router(oauth2_router)
app.add_middleware(OAuth2Middleware, config=oauth2_config)
