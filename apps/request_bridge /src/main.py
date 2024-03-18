import logging
import asyncio
from fastapi import FastAPI, Request, HTTPException
from hoppy import Hoppy, PikaParams, Queues
import uvicorn
from pydantic import BaseModel

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


@api.post("/requests/change_operator")
async def get_operator_info(request: Request):
    async with app:
        data = await request.json()
        operator_id = data["operator_id"]
        operator_name = data["operator_name"]
        transfer_api_url = data["transfer_api_url"]

        # Envío del mensaje a la cola
        await app.send_message(Queues.CHANGE_OPERATORS_QUEUE, {
            "OperatorId": operator_id,
            "OperatorName": operator_name,
            "transferAPIURL": transfer_api_url
        })
    return {"message": "Información del operador enviada a la cola"}

def start():
    setup()
    setup_logging()
    # Start the consumption
    uvicorn.run(api, host="localhost", port=8000)

