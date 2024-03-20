from enum import Enum
from typing import Any, Generic, Optional, TypeVar, Union
from uuid import UUID

from pydantic import BaseModel, EmailStr


class Queues(Enum):
    # User -> register
    START_USER_REGISTER = 'user.start_user_register' 
    PROCESS_USER_VALIADATION = 'user.process_user_validation' 
    DECLINE_USER_REGISTER = 'user.decline_user_register'
    COMPLETE_USER_REGISTER = 'user.complete_user_register'
    CREATE_USER_PASSWORD = 'user.create_user_password'

    #Documents
    UPLOAD_DOCUMENT = 'document.upload_document'

    # Centralizer
    REQUESTS_QUEUE = 'centralizer.requests'

class RegisterUser(BaseModel):
    name: str
    email: EmailStr
    national_id: int
    address: str
    reply_to: Optional[str] = None

class UploadDocument(BaseModel):
    id: UUID 
    filename: str 
    content_type: str 
    size: int 
    md5_hash: str 

class 

class CompleteRegister(BaseModel):
    email: EmailStr
    password: str

class CentralizerRequestType(Enum):
    VALIDATE_CITIZEN = 'validate_citizen'
    REGISTER_CITIZEN = 'register_citizen'


class CentralizerRequest(BaseModel):
    type: CentralizerRequestType
    payload: dict
    reply_to: str


class CentralizerResponse(BaseModel):
    status: int
    message: Optional[Union[str, dict]]
    original_payload: Any
