from fastapi import APIRouter
from fastapi import FastAPI
from fastapi.testclient import TestClient

from fastapi_oauth2.middleware import OAuth2Middleware
from fastapi_oauth2.router import router as oauth2_router

app = FastAPI()
router = APIRouter()

app.include_router(oauth2_router)
app.add_middleware(OAuth2Middleware, config={})

client = TestClient(app)


def test_read_main():
    response = client.get("/")
    assert response.status_code == 404
