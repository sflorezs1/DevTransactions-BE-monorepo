from ast import Dict
import asyncio
import json
import logging
import queue
import ssl
from typing import Any, Callable, Optional, Type
from urllib.parse import quote
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

        # Create async engine with the provided connection string
        self.engine = create_async_engine(db_connection_params.to_connection_string()) if db_connection_params else None

        # Create a configured "AsyncSession" class
        self.AsyncSession = sessionmaker(self.engine, expire_on_commit=False, class_=AsyncSession) if db_connection_params else None

    def consume(self, queue: Queues):
        def decorator(func: QueueHandler):     
            logger.info(f"Consumer registered for queue {queue.value}")
            
            if queue.value in self.consumers:
                raise ValueError(f"Consumer already registered for queue {queue.value}")
            
            self.consumers[queue.value] = func           
            return func
        return decorator

    async def _connect_and_consume(self):
        async def callback(message: aiormq.spec.Basic.Deliver):
            logger.info(f"Processing event {message}")
            session = self.AsyncSession() if self.AsyncSession else None
            try:
                event = Event(message)
                context = Context(session=session)
                handler = self.consumers[message.routing_key]
                await handler(event, context)  # Execute the registered handler
                logger.info(f"Processed message from queue {message.routing_key}")
                await message.ack()
            except Exception as e:
                logger.error(f"Error processing message from queue {message.routing_key}: {e}")
                await message.nack()
            finally:
                await session.close()
        
        logger.info("Connecting and starting consumption...")

        # Create a connection using aio_pika
        connection = await aio_pika.connect_robust(self.connection_params.to_url())
        

        async with connection:
            channel = await connection.channel()

            for queue_name, handler in self.consumers.items():
                try:
                    logger.info(f"Declare queue {queue_name}")
                    queue = await channel.declare_queue(queue_name, durable=False)
                    async with queue.iterator() as queue_iter:
                        async for message in queue_iter:
                            await callback(message)
                except Exception as e:
                    logger.error(f"Error declaring queue {queue_name}: {e}")


    def run(self):
        logger.info("Starting Hoppy...")
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._connect_and_consume())
        loop.run_forever()
