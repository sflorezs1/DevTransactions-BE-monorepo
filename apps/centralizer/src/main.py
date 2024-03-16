import asyncio
import logging

from src.models.user import User
from hoppy import Hoppy, SQLAlchemyParams, PikaParams, Event, Queues, RegisterUserPayload, Context


logger = logging.getLogger(__name__)

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

def register_consumers():
    # Register the consumer for the user creation event
    @app.consume(Queues.REGISTER_CITIZEN)
    async def handle_user_creation(event: Event, context: Context):
        logger.info(f"Received user creation event: {event.body}")
        user_data = event.body   # type: RegisterUserPayload
        db = context.session

        new_user = User(**user_data)
        db.add(new_user)
        await db.commit()

        logger.info(f"Created new user with ID")

def start():
    setup()
    setup_logging()
    # Register the consumers
    register_consumers()
    # Start the consumption
    app.run()