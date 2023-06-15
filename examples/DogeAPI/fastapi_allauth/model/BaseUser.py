import hashlib
import uuid

from sqlalchemy import Column, String

from database.configuration import Base


class BaseUser(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    authority = Column(String)

    payload = ['id', 'authority']

    def __init__(self, id, authority):
        self.id = id
        self.authority = authority

    @classmethod
    def create_authority(cls, open_id, provider):
        context = str(open_id) + provider
        authority = hashlib.sha256(context.encode()).hexdigest()
        return authority

    @classmethod
    def create(
            cls,
            open_id: String,
            provider: String,
    ):
        authority = cls.create_authority(open_id, provider)
        id = uuid.uuid4().hex

        return cls(id=id, authority=authority)

    class Config:
        orm_mode = True

    def __getitem__(self, key):
        return getattr(self, key)


__all__ = [
    "BaseUser"
]
