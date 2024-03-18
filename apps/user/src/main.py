import asyncio
import logging

from .flows.user_registration import user_registration_flow
from hoppy import Hoppy, SQLAlchemyParams, PikaParams, Event, Queues, RegisterUserPayload, Context


logger = logging.getLogger(__name__)

def setup():
    # PikaParams declaration with default values
    pika_params = PikaParams(
        host = "localhost",
        port = 5672,
    )

    # SQLAlchemyParams declaration with default values
    sqlalchemy_params = SQLAlchemyParams(
        username = "postgres",
        password = "postgres",
        host = "localhost",
        port = 5432,
        database = "dt_user",
    )

    # Create the Hoppy instance
    global app
    app = Hoppy(pika_params, sqlalchemy_params)

def setup_logging():
    # Set the logging level for the root logger to DEBUG
    # logging.getLogger().setLevel(logging.DEBUG)

    # Create a console handler
    console_handler = logging.StreamHandler()

    # Set the console handler's level to DEBUG
    # console_handler.setLevel(logging.DEBUG)

    # Create a formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Set the console handler's formatter
    console_handler.setFormatter(formatter)

    # Add the console handler to the root logger
    logging.getLogger().addHandler(console_handler)

def register_consumers():
    user_registration_flow(app)

def start():
    setup()
    setup_logging()
    # Register the consumers
    register_consumers()
    # Start the consumption
    app.run()