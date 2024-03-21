import asyncio
import logging
from faststream import BaseMiddleware, FastStream
from faststream.rabbit import RabbitBroker
from .config import DEBUG, RABBITMQ_URL
from .flows.upload_document import upload_document_flow,get_all_document_flow,get_document_by_id_flow

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

def start():
    setup_logging()
    upload_document_flow(app, broker)
    get_all_document_flow(app, broker)
    get_document_by_id_flow(app, broker)
    asyncio.run(app.run())





