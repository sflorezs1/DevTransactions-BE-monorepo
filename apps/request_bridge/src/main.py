import asyncio
import logging
from fastapi import FastAPI, HTTPException
from h11 import Response
from pydantic import BaseModel, EmailStr
from faststream.rabbit import RabbitBroker
import uvicorn

from queues.queues import Queues, TransferUser, CompleteTransfer

from .config import DEBUG

logger = logging.getLogger(__name__)
broker = RabbitBroker()
api = FastAPI()

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

@api.post("/request/start_request")
async def start_request(user: TransferUser):
    try:
        response = None
        async with broker:
            response = await broker.publish(user, Queues.START_USER_TRANSFER.value, rpc=True)
            logger.info(f"{response=}")
        return response
    except Exception as e:
        raise HTTPException(500, "Internal server error")

@api.post("/request/complete_request")
async def complete_request(user: CompleteTransfer):
    try:
        response = None
        async with broker:
            response = await broker.publish(user, Queues.COMPLETE_USER_TRANSFER.value, rpc=True)
            logger.info(f"{response=}")
        return response
    except Exception as e:
        raise HTTPException(500, "Internal server error")



def start():
    setup_logging()
    uvicorn.run(api, host="0.0.0.0", port=8000)
    