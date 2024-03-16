from dataclasses import dataclass
import json
import logging
from tkinter import SE
from aio_pika import IncomingMessage
from aio_pika.abc import AbstractIncomingMessage
from typing import Generic, TypeVar, Union

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


class Event:
    def __init__(self, message: IncomingMessage):
        self.message = message
        self._parse_body()
    
    def _parse_body(self):
        raw_body = self.message.body
        try:
            # Convert JSON string to object based on T
            parsed_body = json.loads(self.message.body)
            self.body = parsed_body
        except json.JSONDecodeError:
            logger.warn(f"Failed to parse JSON from message body: {self.body}")
            self.body = None
        except Exception as e:
            logger.error(f"Unexpected error parsing message body: {e}")
            self.body = None
        finally:
            self.raw_body = raw_body