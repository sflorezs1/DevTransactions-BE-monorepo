import logging
from typing import List
from auth.api_dependency import ContextAuth, authenticate_token
from fastapi import Depends, FastAPI, HTTPException
from faststream.rabbit import RabbitBroker
import uvicorn

from .config import RABBITMQ_URL
from queues.queues import Queues, UploadDocument

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
    

# @api.get("/documents/all_documents", response_model=List[DocumentBase])
# async def list_documents(session: AsyncSession = Depends(inject_session)):
#     documents = await list_all_documents(session)
#     return documents



@api.get("/documents/{document_id}", response_model=UploadDocument)
async def get_document_by_id(document_id: str):
    try:
        response = None
        async with broker:
            response = await broker.publish({ "document_id": document_id }, Queues.GET_DOCUMENT.value, rpc=True)
            logger.info(f"{response=}")
        return response
    except Exception as e:
        raise HTTPException(500, "Internal server error")

def start():
    setup_logging()
    # Start the consumption
    uvicorn.run(api, host="0.0.0.0", port=8000)


    