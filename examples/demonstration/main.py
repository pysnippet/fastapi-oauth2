from fastapi import APIRouter
from fastapi import FastAPI
from sqlalchemy.orm import Session

from config import oauth2_config
from database import Base
from database import engine
from database import get_db
from fastapi_oauth2.middleware import OAuth2Middleware
from fastapi_oauth2.middleware import User
from fastapi_oauth2.router import router as oauth2_router
from models import User as UserModel
from router import router as app_router

Base.metadata.create_all(bind=engine)

router = APIRouter()


async def on_auth(user: User):
    # perform a check for user existence in
    # the database and create if not exists
    db: Session = next(get_db())
    query = db.query(UserModel)
    if not query.filter_by(identity=user.identity).first():
        UserModel(**{
            "identity": user.get("identity"),
            "username": user.get("username"),
            "image": user.get("image"),
            "email": user.get("email"),
            "name": user.get("name"),
        }).save(db)


app = FastAPI()
app.include_router(app_router)
app.include_router(oauth2_router)
app.add_middleware(OAuth2Middleware, config=oauth2_config, callback=on_auth)
