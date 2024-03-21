import asyncio
import logging
from faststream import BaseMiddleware, FastStream
from faststream.rabbit import RabbitBroker, RabbitQueue

from queues.queues import Queues
from .config import DEBUG, RABBITMQ_URL

from .flows.user_registration import user_registration_flow


logger = logging.getLogger(__name__)

broker = RabbitBroker(RABBITMQ_URL)

app = FastStream(broker)

@app.on_startup()
async def on_startup():
    async with broker:
        for queue in Queues:
            await broker.declare_queue(RabbitQueue(
                name=queue.value,
                durable=False,
                routing_key=queue.value,
            ))     

def setup_logging():
    # Set the logging level for the root logger to DEBUG
    if DEBUG: 
        logging.getLogger().setLevel(logging.DEBUG)
        logging.getLogger("aiormq.connection").setLevel(logging.WARNING)

    # Create a console handler
    console_handler = logging.StreamHandler()

    # Set the console handler's level to DEBUG
    console_handler.setLevel(logging.DEBUG)

    # Create a formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Set the console handler's formatter
    console_handler.setFormatter(formatter)

    # Add the console handler to the root logger
    logging.getLogger().addHandler(console_handler)

def start():
    setup_logging()
    user_registration_flow(app, broker)
    asyncio.run(app.run())

