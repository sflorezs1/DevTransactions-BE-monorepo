import logging
from fastapi import FastAPI, HTTPException
from faststream.rabbit import RabbitBroker
import uvicorn

from queues.queues import Queues, UploadDocument

from .config import DEBUG

logger = logging.getLogger(__name__)
broker = RabbitBroker()
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

@api.post("/document/upload_document")
async def start_upload_document(document: UploadDocument):
    try:
        response = None
        async with broker:
            response = await broker.publish(document, Queues.UPLOAD_DOCUMENT.value, rpc=True)
            logger.info(f"{response=}")
        return response
    except Exception as e:
        raise HTTPException(500, "Internal server error")
    

@api.get("/documents/all_documents", response_model=List[DocumentBase])
async def list_documents(session: AsyncSession = Depends(inject_session)):
    documents = await list_all_documents(session)
    return documents



@api.get("/documents/{document_id}", response_model=UploadDocument)
async def get_document_by_id(document_id: UUID):

    try:
        response = None
        async with broker:
            response = await broker.Consume(document, Queues.UPLOAD_DOCUMENT.value, rpc=True)
            logger.info(f"{response=}")
        return response
    except Exception as e:
        raise HTTPException(500, "Internal server error")
    
    # Publish a request to the document microservice
    request = {"id": document_id}
    await publisher.publish(request, Queues.GET_DOCUMENT.value)

    # Subscribe to the response from the document microservice
    response = await subscriber.subscribe(Queues.GET_DOCUMENT_RESPONSE.value)

    # Return the document or None if not found
    if response and "document" in response:
        return Document(**response["document"])
    else:
        return None

def start():
    setup_logging()
    # Start the consumption
    uvicorn.run(api, host="0.0.0.0", port=8000)


    