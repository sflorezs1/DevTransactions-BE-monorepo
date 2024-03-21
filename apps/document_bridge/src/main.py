import logging
from typing import List
import uuid
from auth.api_dependency import ContextAuth, authenticate_token
from fastapi import Depends, FastAPI, HTTPException
from faststream.rabbit import RabbitBroker
import uvicorn

from .config import RABBITMQ_URL
from queues.queues import Queues, UploadDocument, AllDocuments

from .config import DEBUG

logger = logging.getLogger(__name__)
broker = RabbitBroker(RABBITMQ_URL)
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

@api.post("/document/upload")
async def start_upload_document(document: UploadDocument, user: ContextAuth = Depends(authenticate_token)):
    try:
        response = None
        async with broker:
            response = await broker.publish([document, user], Queues.UPLOAD_DOCUMENT.value, rpc=True)
            logger.info(f"{response=}")
        return response
    except Exception as e:
        raise HTTPException(500, "Internal server error")
    

@api.get("/document/all_documents")
async def list_all_documents(user: ContextAuth = Depends(authenticate_token)):
    try:
        response = None
        async with broker:    
            response = await broker.publish(user, Queues.GET_ALL_DOCUMENTS.value,rpc=True)
            logger.info(f"{response=}")
        if response and "documents" in response:
            return response["documents"]  
        else:
            return []
    except Exception as e:
        raise HTTPException(500, "Internal server error")

@api.get("/document/{document_id}")
async def get_document_by_id(document_id:str, user: ContextAuth = Depends(authenticate_token)):
    logger.debug(f"Procesando solicitud para document_id: {document_id}")
    try:
        async with broker:    
            logger.debug(f"Mensaje enviado a RabbitMQ: {str({"document_id": document_id, "user": user})} ")
            response = await broker.publish(
                [document_id,user], Queues.GET_DOCUMENT_BY_ID.value, rpc=True
            )
            logger.debug("Respuesta recibida de RabbitMQ")
        if response and "document" in response:
            return response["document"]
        else:
            return HTTPException(404, "Documento no encontrado")
    except Exception as e:
        logger.error(f"Error interno del servidor: {str(e)}")
        raise HTTPException(500, "Error interno del servidor")

@api.get("/document/{document_id}")
async def get_document_by_id(document_id:str, user: ContextAuth = Depends(authenticate_token)):
    logger.info(f"Procesando solicitud para document_id: {document_id}")
    try:
        async with broker:    
            logger.info(f"Mensaje enviado a RabbitMQ: {str({"document_id": document_id, "user": user})} ")
            response = await broker.publish(
                [document_id,user], Queues.GET_DOCUMENT_BY_ID.value, rpc=True
            )
            logger.info("Respuesta recibida de RabbitMQ")
        if response and "document" in response:
            return response["document"]
        else:
            return HTTPException(404, "Documento no encontrado")
    except Exception as e:
        logger.error(f"Error interno del servidor: {str(e)}")
        raise HTTPException(500, "Error interno del servidor")
    
    
@api.get("/document/validate/{document_id}")
async def get_document_by_id(document_id:str, user: ContextAuth = Depends(authenticate_token)):
    try:
        async with broker:
            response = await broker.publish(
                [document_id,user], Queues.VALIDATE_DOCUMENT.value, rpc=True
            )
        if response and "validated" in response:
            return response["validated"]
        else:
            return HTTPException(404, "Documento no encontrado")
    except Exception as e:
        raise HTTPException(500, "Error interno del servidor")


def start():
    setup_logging()
    # Start the consumption
    uvicorn.run(api, host="0.0.0.0", port=8000)
