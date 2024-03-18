from dataclasses import dataclass
import json
import logging
from aio_pika import IncomingMessage
from aio_pika.abc import AbstractIncomingMessage
from typing import Generic, TypeVar, Union
from pydantic import BaseModel, ValidationError
from typing import Any

from .queues import Queues

logger = logging.getLogger(__name__)

# Define a type variable T that must be a subclass of Queues
T = TypeVar('T', bound=Queues)


# Define the expected body structure for each queue
@dataclass
class RegisterUserPayload:
    email: str
    password: str

@dataclass
class TransferUserPayload:
    national_id: str
    selected_operator: str


# Map queue types to body types
QueueBodyType = Union[RegisterUserPayload, TransferUserPayload]

class RegisterUserContract(BaseModel):
    email: str
    password: str

class TransferUserContract(BaseModel):
    national_id: str
    selected_operator: str

def validate_contract(queue: Queues, body: dict) -> Any:
    return body
    try:
        match queue:
            case Queues.REGISTER_USER:
                return RegisterUserContract.model_validate(body)
            case Queues.TRANSFER_USER:
                return TransferUserContract.model_validate(body)
            case _:
                raise ValueError(f"Unknown queue: {queue}")
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
            # Convert JSON string to object based on T
            parsed_body = json.loads(self.message.body.decode())
            logger.info(f"parsed_body: {self.message.body} as {parsed_body}")
            self.body = parsed_body
        except json.JSONDecodeError:
            logger.warn(f"Failed to parse JSON from message body: {self.message.body}")
            self.body = None
        except Exception as e:
            logger.error(f"Unexpected error parsing message body: {e}")
            self.body = None
        finally:
            self.raw_body = raw_body