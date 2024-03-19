from ast import parse
from collections import namedtuple
from dataclasses import dataclass
import json
import logging
from aio_pika import IncomingMessage
from aio_pika.abc import AbstractIncomingMessage
from typing import Generic, TypeVar, Union
from pydantic import BaseModel, EmailStr, ValidationError
from typing import Any

from .queues import Queues

logger = logging.getLogger(__name__)

# Define a type variable T that must be a subclass of Queues
T = TypeVar('T', bound=Queues)


# Define the expected body structure for each queue
@dataclass
class RegisterUserPayload:
    name: str
    email: str
    national_id: int
    address: str
    operator_id: str
    operator_name: str

@dataclass
class TransferUserPayload:
    national_id: str
    selected_operator: str

@dataclass
class CentralizerResponsePayload:
    status: int
    message: str

@dataclass
class CreatePasswordPayload:
    email: str
    password: str

# Map queue types to body types
QueueBodyType = Union[RegisterUserPayload, TransferUserPayload, CentralizerResponsePayload]

class RegisterUserContract(BaseModel):
    name: str
    email: EmailStr
    national_id: int
    address: str
    operator_id: str
    operator_name: str


class CreatePasswordContract(BaseModel):
    email: EmailStr
    password: str

class TransferUserContract(BaseModel):
    national_id: str
    selected_operator: str

class CentralizerResponsePayload(BaseModel):
    original_payload: Any  # is a dataclass
    status: int
    message: str

def validate_contract(queue: Queues, body: dict) -> Any:
    try:
        match queue:
            case Queues.START_USER_REGISTER:
                return RegisterUserContract.model_validate(body)
            case Queues.PROCESS_USER_VALIADATION:
                return CentralizerResponsePayload.model_validate(body)
            case _:
                logger.info(f"Will not validate payload for queue {queue} as it is not known, may be a reply queue")
    except ValidationError as e:
        print(f"Validation error for queue {queue}: {e}")
        return None

class Event:
    def __init__(self, message: IncomingMessage):
        self.message = message
        self.body = None
        self.raw_body = None
        self._parse_body()
    
    def _parse_body(self):
        raw_body = self.message.body
        try:
            validate_contract(self.message.routing_key, raw_body)
            parsed_body = json.loads(self.message.body.decode())
            logger.info(f"parsed_body: {self.message.body} as {parsed_body}")
            DynamicNamedTuple = namedtuple('DynamicNamedTuple', parsed_body.keys())
            self.body = DynamicNamedTuple(**parsed_body)
        except json.JSONDecodeError:
            logger.warn(f"Failed to parse JSON from message body: {self.message.body}")
            self.body = None
        except Exception as e:
            logger.error(f"Unexpected error parsing message body: {e}")
            self.body = None
        finally:
            self.raw_body = raw_body