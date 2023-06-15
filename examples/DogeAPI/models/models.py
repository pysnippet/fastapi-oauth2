#!/usr/bin/python3
from fastapi_allauth.model import BaseUser
from sqlalchemy import Column, Integer, String

from database.configuration import Base


class Blog(Base):
    """
    Blog class

    Args:
        Base (sqlalchemy.ext.declarative.api.Base): Base class
    """

    __tablename__ = "blogs"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    body = Column(String)


class User(BaseUser):
    """
    User class

    Args:
        Base (sqlalchemy.ext.declarative.api.Base): Base class
    """

    name = Column(String)
    email = Column(String)
    password = Column(String)
