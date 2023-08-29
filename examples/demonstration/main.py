from fastapi import APIRouter
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from config import oauth2_config
from database import Base
from database import engine
from database import get_db
from fastapi_oauth2.middleware import Auth
from fastapi_oauth2.middleware import OAuth2Middleware
from fastapi_oauth2.middleware import User
from fastapi_oauth2.router import router as oauth2_router
from models import User as UserModel
from router_api import router_api
from router_ssr import router_ssr

Base.metadata.create_all(bind=engine)

router = APIRouter()


async def on_auth(auth: Auth, user: User):
    # perform a check for user existence in
    # the database and create if not exists
    db: Session = next(get_db())
    query = db.query(UserModel)
    if user.identity and not query.filter_by(identity=user.identity).first():
        # create a local user by OAuth2 user's data if it does not exist yet
        UserModel(**{
            "identity": user.identity,  # User property
            "username": user.get("username"),  # custom attribute
            "name": user.display_name,  # User property
            "image": user.picture,  # User property
            "email": user.email,  # User property
        }).save(db)


app = FastAPI()
app.include_router(router_api)
app.include_router(router_ssr)
app.include_router(oauth2_router)
app.mount("/static", StaticFiles(directory="static"), name="static")
app.add_middleware(OAuth2Middleware, config=oauth2_config, callback=on_auth)
