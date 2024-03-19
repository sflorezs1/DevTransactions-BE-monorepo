import uuid
from sqlalchemy import Column, Integer, String, cast, Enum as SQLAEnum
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.hybrid import hybrid_property
from enum import Enum

from . import Base


class StateEnum(Enum):
    ACTIVE = 'active'
    INACTIVE = 'inactive'
    SUSPENDED = 'suspended'


class User(Base):
    __tablename__ = "users"

    id = Column(postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True)
    name = Column(String, nullable=False)
    _national_id = Column('national_id', String, nullable=False)
    address = Column(String, nullable=False)
    state = Column(String, nullable=False, default=StateEnum.INACTIVE.value)

    @hybrid_property
    def national_id(self):
        return int(self._national_id)

    @national_id.setter
    def national_id(self, value):
        self._national_id = str(value)

    @national_id.expression
    def national_id(cls):
        return cast(cls._national_id, Integer)
