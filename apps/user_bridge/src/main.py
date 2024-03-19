import asyncio
import logging
from fastapi import FastAPI
from pydantic import BaseModel, EmailStr
import uvicorn

from hoppy import Hoppy, SQLAlchemyParams, PikaParams, Event, Queues, RegisterUserPayload, Context


logger = logging.getLogger(__name__)
api = FastAPI()

def setup():
    # PikaParams declaration with default values
    pika_params = PikaParams(
        host = "localhost",
        port = 5672,
    )

    # Create the Hoppy instance
    global app
    app = Hoppy(pika_params)

def setup_logging():
    # Set the logging level for the root logger to DEBUG
    logging.getLogger().setLevel(logging.DEBUG)

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


class RegisterUser(BaseModel):
    name: str
    email: EmailStr
    national_id: int
    address: str
    operator_id: str
    operator_name: str

class CompleteRegister(BaseModel):
    email: EmailStr
    password: str

@api.post("/user/start_register")
async def start_register(user: RegisterUser):
    async with app:
        reply_queue = await app.send_message(Queues.START_USER_REGISTER, user.model_dump(), True)
        response = await app.consume_once_and_destroy(reply_queue)
    return response

@api.post("/user/complete_register")
async def start_register(info: CompleteRegister):
    async with app:
        reply_queue = await app.send_message(Queues.CREATE_USER_PASSWORD, info.model_dump(), True)
        response = await app.consume_once_and_destroy(reply_queue)
    return response

def start():
    setup()
    setup_logging()
    # Start the consumption
    uvicorn.run(api, host="0.0.0.0", port=8000)
    