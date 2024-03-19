from sqlalchemy import Column, Integer, String, DateTime, BigInteger
from sqlalchemy.dialects import postgresql
import uuid
import datetime

from . import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filename = Column(String(255), nullable=False)
    content_type = Column(String(255))
    size = Column(BigInteger)
    gcs_path = Column(String(1024), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.now(datetime.UTC))
    updated_at = Column(DateTime, onupdate=datetime.datetime.now(datetime.UTC))
    md5_hash = Column(String(32)) 
