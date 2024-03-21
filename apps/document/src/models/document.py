from sqlalchemy import Column, Integer, String, DateTime, BigInteger
from sqlalchemy.dialects import postgresql
import uuid
import datetime

from . import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filename = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    gcs_path = Column(String(1024), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.datetime.utcnow)
