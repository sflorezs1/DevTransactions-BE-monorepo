from fastapi import FastAPI, Body
import logging
from pydantic import BaseModel
from hoppy import Hoppy, PikaParams, Queues
import uvicorn

# Parámetros de conexión a Hoppy (adapta a los tuyos)
pika_params = PikaParams()
app = Hoppy(pika_params)

logger = logging.getLogger(__name__)
api = FastAPI()

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

class DocumentInfo(BaseModel):
    name: str
    document_type: str


@api.post("/documents")
async def upload_document_info(documentinfo=DocumentInfo):
    # Preparación del mensaje para RabbitMQ
    message_body = {
        "nombre_documento": documentinfo.name,
        "tipo_documento": documentinfo.document_type,
    }

    # Envío del mensaje a RabbitMQ
    await app.send_message(Queues.DOCUMENTS_QUEUE, message_body)

    return {"message": f"Información del documento enviada a la cola"}

def start():
    setup_logging()
    uvicorn.run(api, host="localhost", port=8000)



