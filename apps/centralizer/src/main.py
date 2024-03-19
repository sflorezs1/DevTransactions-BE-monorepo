import asyncio
import logging
from typing import Any, Generic
from faststream import BaseMiddleware, FastStream
from faststream.rabbit import RabbitBroker
from src.adapter import GovCarpetaAPIAdapter
from .config import DEBUG, RABBITMQ_URL

from queues.queues import CentralizerRequest, CentralizerRequestType, CentralizerResponse, Queues, RegisterUser

logger = logging.getLogger(__name__)

broker = RabbitBroker(RABBITMQ_URL)

app = FastStream(broker)

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

@broker.subscriber(Queues.REQUESTS_QUEUE.value)
async def handle_request(msg: CentralizerRequest):
    adapter = GovCarpetaAPIAdapter()
    match msg.type:
        case CentralizerRequestType.VALIDATE_CITIZEN:
            logger.info(f"Received request to validate citizen: {msg.payload}")
            response = await adapter.validate_citizen(msg.payload["id"])

        case CentralizerRequestType.REGISTER_CITIZEN:
            logger.info(f"Received request to register citizen: {msg.payload}")
            response = await adapter.register_citizen(msg.payload)
            
        case "delete_user":
            logger.info(f"Received request to delete user: {msg.payload}")
            response = await adapter.unregister_citizen(msg.payload)
            
        case _:
            logger.warning(f"Received unknown request type: {msg.type}")
    await broker.publish(CentralizerResponse(
        status=response["status"],
        message=response["data"],
        original_payload=msg.payload,
    ), msg.reply_to)

def start():
    setup_logging()
    asyncio.run(app.run())
