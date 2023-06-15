from sqlalchemy.orm import Session

from ..model.BaseUser import BaseUser


def register(db: Session, user: BaseUser):
    db.add(user)
    db.commit()
    db.refresh(user)

    return user
