import uuid
from sqlalchemy import Column, Integer, String
from sqlalchemy.dialects import postgresql

from . import Base


class User(Base):
    __tablename__ = "users"

    id = Column(postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String)
    email = Column(String, unique=True, index=True)
