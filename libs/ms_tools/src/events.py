from dataclasses import dataclass

from .queues import MessageQueues

@dataclass
class Event:
    queue: MessageQueues
    body: dict  # Assuming you'll be handling JSON-like data
