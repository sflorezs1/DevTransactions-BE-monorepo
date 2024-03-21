import asyncio
import logging
from typing import Any, Generic
from faststream import BaseMiddleware, FastStream
from faststream.rabbit import RabbitBroker, RabbitQueue
from src.adapter import GovCarpetaAPIAdapter
from .config import DEBUG, RABBITMQ_URL, MOCK_CENTRALIZER

from queues.queues import CentralizerRequest, CentralizerRequestType, CentralizerResponse, Queues, RegisterUser

logger = logging.getLogger(__name__)

broker = RabbitBroker(RABBITMQ_URL)

app = FastStream(broker)

@app.on_startup
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

@broker.subscriber(Queues.REQUESTS_QUEUE.value)
async def handle_request(msg: CentralizerRequest):
    if MOCK_CENTRALIZER:
        logger.info("Mock centralizer is enabled")
        await broker.publish(CentralizerResponse(
            status=204 if msg.type == CentralizerRequestType.VALIDATE_CITIZEN else 201 if msg.type == CentralizerRequestType.REGISTER_CITIZEN else 200,
            message="Mock centralizer is enabled",
            original_payload=msg.payload,
        ), msg.reply_to)
        return
    
    adapter = GovCarpetaAPIAdapter()
    match msg.type:
        case CentralizerRequestType.VALIDATE_CITIZEN:
            logger.info(f"Received request to validate citizen: {msg.payload}")
            response = await adapter.validate_citizen(msg.payload["id"])

        case CentralizerRequestType.REGISTER_CITIZEN:
            logger.info(f"Received request to register citizen: {msg.payload}")
            response = await adapter.register_citizen(msg.payload)
            
        case CentralizerRequestType.UNREGISTER_CITIZEN:
            logger.info(f"Received request to unregister user: {msg.payload}")
            response = await adapter.unregister_citizen(msg.payload)

        case CentralizerRequestType.GET_OPERATORS:  
            logger.info(f"Received request to get operators")
            response = await adapter.get_operators()
            
        case _:
            logger.warning(f"Received unknown request type: {msg.type}")
    
    if msg.reply_to is not None and msg.reply_to != '':
        async with broker:
            await broker.publish(CentralizerResponse(
                status=response["status"],
                message=response["data"],
                original_payload=msg.payload,
            ), msg.reply_to)
    else:
        return CentralizerResponse(
            status=response["status"],
            message=response["data"],
            original_payload=msg.payload,
        )

def start():
    setup_logging()
    asyncio.run(app.run())
