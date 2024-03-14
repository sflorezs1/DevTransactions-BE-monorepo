import asyncio
import json
from typing import Callable
import pika
from sqlalchemy.ext.asyncio import AsyncSession
from .events import Event
from .database import DatabaseAdapter
from .queues import MessageQueues



class Hoppy:
    def __init__(self, name: str, rabbitmq_host: str, rabbitmq_port: int, database_adapter: DatabaseAdapter):
        self._connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=rabbitmq_host, port=rabbitmq_port)
        )
        self.name = name
        self._channel = self._connection.channel()
        self._message_handlers = {}
        self._database_adapter = database_adapter

    def queue_listener(self, queue_enum: MessageQueues) -> Callable[[Event, AsyncSession], None]:
        def decorator(func):
            self._message_handlers[queue_enum] = func
            return func
        return decorator

    async def start(self):
        async with self._database_adapter.get_async_session() as db_session: 
            for queue_enum, handler in self._message_handlers.items():
                self._channel.queue_declare(queue=queue_enum.value)

                def callback(ch, method, properties, body):
                    event = Event(queue=queue_enum, body=json.loads(body))
                    asyncio.create_task(handler(event, db_session))  

                self._channel.basic_consume(queue=queue_enum.value, on_message_callback=callback, auto_ack=True)

            self._channel.start_consuming()
