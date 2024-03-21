from enum import Enum
import operator
from typing import Any, Generic, List, Optional, TypeVar, Union

from pydantic import BaseModel, EmailStr


class Queues(Enum):
    # User -> register
    START_USER_REGISTER = 'user.start_user_register' 
    PROCESS_USER_VALIADATION = 'user.process_user_validation' 
    DECLINE_USER_REGISTER = 'user.decline_user_register'
    COMPLETE_USER_REGISTER = 'user.complete_user_register'
    CREATE_USER_PASSWORD = 'user.create_user_password'

    # User -> transfer
    ADD_USER_TRANSFER_INFO = 'user.add_user_transfer_info'
    
    # Centralizer
    REQUESTS_QUEUE = 'centralizer.requests'

    # Document
    UPLOAD_DOCUMENT = 'document.upload_document'
    ADD_USER_TRANSFER_DOCS_INFO = 'user.add_user_transfer_docs_info'

    # Request
    START_USER_TRANSFER = 'user.start_user_transfer'
    COMPLETE_USER_TRANSFER = 'user.complete_user_transfer' 


class RegisterUser(BaseModel):
    name: str
    email: EmailStr
    national_id: int
    address: str
    reply_to: Optional[str] = None = None


class CompleteRegister(BaseModel):
    email: EmailStr
    password: str


class CentralizerRequestType(Enum):
    VALIDATE_CITIZEN = 'validate_citizen'
    REGISTER_CITIZEN = 'register_citizen'
    UNREGISTER_CITIZEN = 'unregister_citizen'
    GET_OPERATORS = 'get_operators'


class CentralizerRequest(BaseModel):
    type: CentralizerRequestType
    payload: dict
    reply_to: Optional[str] = None


class UploadDocument(BaseModel):
    filename: str 
    content_type: str 
    size: int 
    md5_hash: str


class TransferRequestPayload(BaseModel):
    operator_id: str


class CentralizerResponse(BaseModel):
    status: int
    message: Optional[Union[str, dict]]
    original_payload: Any


class OperatorInfo(BaseModel):
    operator_id: Optional[str] = None
    operator_name: Optional[str] = None
    operator_transfer_url: Optional[str] = None


class TransferFilePayload(BaseModel):
    document_title: str
    url_document: str


class TransferUserPayload(BaseModel):
    id: Optional[int] = None
    email: str
    name: Optional[str] = None
    addres: Optional[str] = None
    callback_url: Optional[str] = None
    files: Optional[List[TransferFilePayload]] = []


class CompleteTransferPayload(BaseModel):
    user_id: int
