import asyncio
import logging
from auth.api_dependency import ContextAuth
from fastapi import Depends, FastAPI, HTTPException
from h11 import Response
from pydantic import BaseModel, EmailStr
from faststream.rabbit import RabbitBroker, RabbitQueue
import uvicorn

from queues.queues import Queues, TransferRequestPayload, TransferUserCammelPayload
from auth.api_dependency import authenticate_token

from .config import DEBUG

logger = logging.getLogger(__name__)
broker = RabbitBroker()
api = FastAPI()

@api.get('/')
def health_check():
    return {"status": "ok"}

@api.on_event("startup")
async def on_startup():
    async with broker:
        for queue in Queues:
            await broker.declare_queue(RabbitQueue(
                name=queue.value,
                durable=True,
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

@api.post("/request/start_transfer")
async def start_transfer(request: TransferRequestPayload, auth: ContextAuth = Depends(authenticate_token)):
    try:
        response = None
        async with broker:
            response = await broker.publish([request, auth], Queues.START_USER_TRANSFER.value, rpc=True)
            logger.info(f"{response=}")
        return response
    except Exception as e:
        raise HTTPException(500, "Internal server error")

@api.post("/request/complete_transfer")
async def complete_request(msg):
    try:
        response = None
        async with broker:
            await broker.publish(msg, Queues.ACK_USER_TRANSFER.value)
            logger.info(f"{response=}")
        return response
    except Exception as e:
        raise HTTPException(500, "Internal server error")


@api.post("/request/transfer_citizen")
async def complete_request(payload: TransferUserCammelPayload):
    try:
        response = None
        async with broker:
            await broker.publish(payload, Queues.ENQUEUE_TRANSFER_CITIZEN.value)
            logger.info(f"{response=}")
        return {
            "message": "User transfer enqueued successfully",
        }
    except Exception as e:
        raise HTTPException(500, "Internal server error")


def start():
    setup_logging()
    uvicorn.run(api, host="0.0.0.0", port=8000)
    