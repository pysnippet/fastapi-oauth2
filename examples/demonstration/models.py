from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import Session

from database import Base


class BaseModel(Base):
    __abstract__ = True

    def save(self, db: Session):
        db.add(self)
        db.commit()
        db.refresh(self)
        return self


class User(BaseModel):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String)
