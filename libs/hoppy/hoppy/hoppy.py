from ast import Dict
import asyncio
from asyncio import tasks
from dataclasses import asdict, dataclass, is_dataclass
from email import message
import json
import logging
import queue
import ssl
import time
from typing import Any, Callable, NamedTuple, Optional, Type, Union
from urllib.parse import quote
import uuid
import aio_pika
import aiormq
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from aio_pika.abc import AbstractConnection

from .queues import Queues
from .event import Event

# Create a logger
logger = logging.getLogger(__name__)

logger.setLevel(logging.DEBUG)

# Create a console handler
console_handler = logging.StreamHandler()

# Set the console handler's level to DEBUG
console_handler.setLevel(logging.DEBUG)

# Create a formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Set the console handler's formatter
console_handler.setFormatter(formatter)

# Add the console handler to the logger
logger.addHandler(console_handler)

class PikaParams:
    def __init__(
        self,
        url: Optional[str] = None,
        host: str = "localhost",
        port: int = 5672,
        login: str = None,
        password: str = None,
        virtualhost: str = "/",
    ):
        self.url: Optional[str] = url
        self.host: str = host
        self.port: int = port
        self.login: str = login
        self.password: str = password
        self.virtualhost: str = virtualhost
        
    def to_url(self) -> str:
        # Quote the login and password to ensure they are URL-safe
        # login = quote(self.login, safe='')
        # password = quote(self.password, safe='')

        # Construct the URL
        url = f"amqp://{self.host}:{self.port}/"
        return url
 

class SQLAlchemyParams:
    def __init__(
        self,
        username: str = "user",
        password: str = "password",
        host: str = "localhost",
        port: int = 5432,
        database: str = "dbname",
    ):
        self.username: str = username
        self.password: str = password
        self.host: str = host
        self.port: int = port
        self.database: str = database

    def to_connection_string(self):
        return f"postgresql+asyncpg://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"


class Context:
    def __init__(self, session: AsyncSession):
        self.session = session
        # You can add more attributes here if needed


QueueHandler = Callable[[Event, Context], None]


class Hoppy:
    def __init__(self, connection_params: PikaParams, db_connection_params: SQLAlchemyParams = None):
        self.connection_params = connection_params
        self.consumers: Dict[Queues, QueueHandler] = {}
        self.connection: Optional[AbstractConnection] = None
        # Create async engine with the provided self.connection string
        self.engine = create_async_engine(db_connection_params.to_connection_string()) if db_connection_params else None

        # Create a configured "AsyncSession" class
        self.AsyncSession = sessionmaker(self.engine, expire_on_commit=False, class_=AsyncSession) if db_connection_params else None

    async def __aenter__(self):
        # Perform setup tasks here, if any
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # Perform cleanup tasks here, such as closing connections
        if self.connection:
            await self.connection.close()

    def consume(self, queue: Queues):
        def decorator(func: QueueHandler):     
            logger.info(f"Consumer registered for queue {queue.value}")
            
            if queue.value in self.consumers:
                raise ValueError(f"Consumer already registered for queue {queue.value}")
            
            self.consumers[queue.value] = func           
            return func
        return decorator

    async def connect(self):
        # Create a self.connection using aio_pika
        self.connection = await aio_pika.connect_robust(self.connection_params.to_url())

    async def disconnect(self):
        if self.connection is not None:
            await self.connection.close()
            self.connection = None

    async def _callback(self, message: aiormq.spec.Basic.Deliver, handler):
        logger.info(f"Processing event {message}")
        session = self.AsyncSession() if self.AsyncSession else None
        response = None
        try:
            event = Event(message)
            context = Context(session=session)
            response = await handler(event, context)  # Execute the registered handler
            logger.info(f"Processed message from queue {message.routing_key}")
            await message.ack()
        except Exception as e:
            logger.error(f"Error processing message from queue {message.routing_key}: {e}")
            await message.nack()
        finally:
            if session:
                await session.close()
        return response

    async def _connect_and_consume(self):
        async def callback(message: aiormq.spec.Basic.Deliver):
            await self._callback(message, self.consumers[message.routing_key])
        
        logger.info("Connecting and starting consumption...")

        if self.connection is None:
            await self.connect()

        channel = await self.connection.channel()

        async def handle_queue(queue_name, handler):
            try:
                logger.info(f"Declare queue {queue_name}")
                queue = await channel.declare_queue(queue_name, durable=False)
                async with queue.iterator() as queue_iter:
                    async for message in queue_iter:
                        await callback(message)
            except Exception as e:
                logger.error(f"Error declaring queue {queue_name}: {e}")

        tasks = []

        for queue_name, handler in self.consumers.items():
            # Create a new task for each queue
            task = asyncio.create_task(handle_queue(queue_name, handler))
            tasks.append(task)

        await asyncio.gather(*tasks)
        
        await self.disconnect()

    async def send_message(self, queue: Queues, message_body, create_reply_queue: bool = False, auto_close: bool = True):
        # Create a self.connection using aio_pika
        if self.connection is None:
            await self.connect()

        reply_queue_name = None

        queue = queue.value if isinstance(queue, Queues) else queue

        # Creating a channel
        channel = await self.connection.channel()

        # Declare a queue
        queue = await channel.declare_queue(queue, durable=False)

        body = asdict(message_body) if is_dataclass(message_body) else message_body
        # Create a reply queue if requested
        if create_reply_queue:
            reply_queue_name = str(uuid.uuid4())
            reply_queue = await channel.declare_queue(reply_queue_name, auto_delete=True, timeout=30)
            body = { **message_body, "reply_to": reply_queue_name }

        # Send the message
        await channel.default_exchange.publish(
            aio_pika.Message(body=json.dumps(body).encode()),
            routing_key=queue.name,
        )

        if auto_close:
            await self.disconnect()

        logger.info(f"Sent message to queue {queue.name}")

        return reply_queue_name
    
    async def consume_once_and_destroy(self, queue_name: Union[str, Queues], auto_close: bool = True):
        if self.connection is None:
            await self.connect()

        queue_name = queue_name.value if isinstance(queue_name, Queues) else queue_name
        response = None
        channel = await self.connection.channel() 
        # Create a temporary queue
        temp_queue = await channel.declare_queue(queue_name, auto_delete=True)

        # Consume a message from the queue
        message = await asyncio.wait_for(temp_queue.iterator().__anext__(), 30)

        try:
            response = await self._callback(message, lambda _, __: _.body)
            # Acknowledge the message
            await temp_queue.ack(message.delivery_tag)

            logger.info(f"Message from {queue_name} processed and acknowledged")

        except Exception as e:
            logger.error(f"Error processing message from {queue_name}: {e}")

        finally:
            # Delete the queue
            await temp_queue.delete()

        logger.info(f"Queue {queue_name} deleted after consuming message")
        if auto_close:
            await self.disconnect()

        return response

    def run(self):
        logger.info("Starting Hoppy...")
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._connect_and_consume())
        loop.run_forever()
