import logging
import json
from hoppy import Hoppy, PikaParams, Queues
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import sessionmanager,DATABASE_URL
from src.models import Document 

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

@app.consume(Queues.DOCUMENTS_QUEUE)
def process_document_info(message):
    """
    Consume el mensaje de la cola y procesa la información del documento
    """
    try:
        # Convierte la información recibida a JSON
        document_info = json.loads(message.body)

        # Crea una sesión con la base de datos 
        session = Session()

        # Crea una instancia del modelo Document
        document = Document(
            filename=document_info["nombre_documento"],
            content_type="Inferir tipo de contenido",  # Necesitas agregarlo
            size=0,  # Necesitas agregarlo
            gcs_path="Pendiente de subida", # Se actualizaría luego 
            md5_hash="Pendiente de cálculo"  # Se calcularía luego
        )

        # Agrega el documento a la sesión
        session.add(document)
        session.commit()  

        logger.info(f"Documento procesado correctamente: {document.id}")

    except Exception as e:
        logger.error(f"Error al procesar el documento: {e}")


def start():
    setup()
    setup_logging()
    app.start()  # Inicia Hoppy para consumir la cola 