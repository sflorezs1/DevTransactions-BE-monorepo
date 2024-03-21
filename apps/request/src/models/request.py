import uuid
from sqlalchemy import Column, Integer, String, cast, Enum as SQLAEnum
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.hybrid import hybrid_property
from enum import Enum

from . import Base


class TransferStatus(Enum):
    ACTIVE = 'active'
    INACTIVE = 'inactive'
    SUSPENDED = 'suspended'


class OperatorTransferRequest(Base):
    __tablename__ = "operator_transfer_requests"

    id = Column(postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id = Column(String, unique=True, index=True)
    operator_id = Column(String, nullable=False)  
    state = Column(String, nullable=False, default=TransferStatus.INACTIVE.value)

