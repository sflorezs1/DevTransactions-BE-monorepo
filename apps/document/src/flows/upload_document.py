import datetime
import email
import logging
import uuid

from src.config import RABBITMQ_URL
from auth.api_dependency import ContextAuth
from cryptography.fernet import Fernet
from faststream import Depends, FastStream
from faststream.rabbit import RabbitBroker
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from ..config import SQLALCHEMY_DATABASE_URI
from queues.queues import  CentralizerRequest, CentralizerRequestType, OperatorInfo, Queues, TransferFilePayload, TransferUserPayload, UploadDocument
from db.db import get_db_dependency
from ..models.document import Document
from ..document.adapter import GCPStorageAdapter


logger = logging.getLogger(__name__)

inject_session = get_db_dependency(SQLALCHEMY_DATABASE_URI)

def upload_document_flow(app: FastStream, broker: RabbitBroker):
    @broker.subscriber(Queues.UPLOAD_DOCUMENT.value)
    async def handle_document_creation(msg: UploadDocument, auth: ContextAuth, session: AsyncSession = Depends(inject_session)):
        logger.info(f"Received document creation event: {msg}")
        adapter = GCPStorageAdapter()
        document_info = msg

        document = Document(
            filename = document_info.filename,
            content_type = document_info.content_type,
            size = document_info.size,
            md5_hash = document_info.md5_hash,
            gcs_path = f"{auth.email}/{document_info.filename}",
            email = auth.email,
        )
        session.add(document)
        await session.commit()
        
        url=adapter.generate_presigned_put_url(document.gcs_path,expiration=datetime.timedelta(minutes=5))
       
        return {
            "url": url
        }
    
def get_all_document_flow(app: FastStream, broker: RabbitBroker):
    @broker.subscriber(Queues.GET_ALL_DOCUMENTS.value)
    async def handle_get_all_documents(auth: ContextAuth, session: AsyncSession = Depends(inject_session)):
        documents = await session.execute(select(Document).where(Document.email==auth.email))
        documents = documents.scalars().all()
        
        logger.info(f"documents: {documents}")
        return {"documents":[{ "id": x.id, "filename": x.filename } for x in documents]}
    
    
    
def get_document_by_id_flow(app: FastStream, broker: RabbitBroker):
    @broker.subscriber(Queues.GET_DOCUMENT_BY_ID.value)
    async def handle_get_document_by_id( document_id: str,auth: ContextAuth,session: AsyncSession = Depends(inject_session)):       

        document = await session.execute(select(Document).where(Document.id == document_id, and_(Document.email==auth.email)))
        document = document.scalar_one_or_none()
        adapter = GCPStorageAdapter()
        url=adapter.generate_presigned_get_url(document.gcs_path,expiration=datetime.timedelta(minutes=10))

        if document:
            return {"document":{
                "filename":document.filename,
                "id":document.id,
                "url":url
            }}
        else:
            return None
        

def operator_transfer_add_files(app: FastStream, broker: RabbitBroker):
    @broker.subscriber(Queues.ADD_USER_TRANSFER_DOCS_INFO.value)
    async def handle_user_transfer_docs_info(transfer_payload: TransferUserPayload, operator_info: OperatorInfo, session: AsyncSession = Depends(inject_session)):
        logger.info(f"Received user transfer event: {transfer_payload}")

        query = await session.execute(select(Document).filter(Document.email == transfer_payload.email))
        documents = query.scalars().all()

        if not documents:
            documents = []
        
        for document in documents:
            doc = TransferFilePayload(
                document_title=document.filename,
                url_document=document.gcs_path
            )
            transfer_payload.documents.append(doc)

        async with broker:
            await broker.publish([transfer_payload, operator_info], Queues.COMPLETE_USER_TRANSFER.value)

def validate_document(app: FastStream, broker: RabbitBroker):
    @broker.subscriber(Queues.ADD_USER_TRANSFER_DOCS_INFO.value)
    async def handle_validate_document(document_id: str, auth: ContextAuth, session: AsyncSession = Depends(inject_session)):
        
        document = await session.execute(select(Document).where(Document.id == document_id, and_(Document.email==auth.email)))
        document = document.scalar_one_or_none()
        adapter = GCPStorageAdapter()
        url = adapter.generate_presigned_get_url(document.gcs_path, expiration=datetime.timedelta(minutes=10))

        async with broker:
            user = await broker.publish(auth.id, Queues.GET_USER.value, rpc=True)

        centralizer_payload = CentralizerRequest(
            type=CentralizerRequestType.VALIDATE_DOCUMENT,
            payload={
                "idCard": user["national_id"],
                "urlDocument": url,
                "documentTitle": document.filename
            }
        )

        async with broker:
            response = await broker.publish(centralizer_payload, Queues.REQUESTS_QUEUE.value, rpc=True)

        if response and "status" in response and response["status"] == 200:
            return {
                "validated": True
            }
        else:
            return None
