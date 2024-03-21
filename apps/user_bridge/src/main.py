import asyncio
import logging
from auth.firebase_auth import authenticate_user
from fastapi import FastAPI, HTTPException
from h11 import Response
from pydantic import BaseModel, EmailStr
from faststream.rabbit import RabbitBroker, RabbitQueue
import uvicorn

from .config import RABBITMQ_URL
from queues.queues import CompleteRegister, Queues, RegisterUser

from .config import DEBUG

logger = logging.getLogger(__name__)
broker = RabbitBroker(RABBITMQ_URL)
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

@api.post("/user/start_register")
async def start_register(user: RegisterUser):
    try:
        response = None
        async with broker:
            response = await broker.publish(user, Queues.START_USER_REGISTER.value, rpc=True)
            logger.info(f"{response=}")
        return response
    except Exception as e:
        raise HTTPException(500, "Internal server error")

@api.post("/user/complete_register")
async def complete_register(info: CompleteRegister):
    try:
        response = None
        async with broker:
            response = await broker.publish(info, Queues.CREATE_USER_PASSWORD.value, rpc=True)
            logger.info(f"{response=}")
        return response
    except Exception as e:
        raise HTTPException(500, "Internal server error")

class UserCredentials(BaseModel):
    email: str
    password: str

@api.post("/user/login")
async def login(credentials: UserCredentials):
    authenticated = await authenticate_user(credentials.email, credentials.password)
    if authenticated:
        return {"token": authenticated}
    else:
        raise HTTPException(401, "Invalid credentials")


def start():
    setup_logging()
    # Start the consumption
    uvicorn.run(api, host="0.0.0.0", port=8000)
    