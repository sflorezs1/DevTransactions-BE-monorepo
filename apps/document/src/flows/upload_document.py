import datetime
import logging
from os import name
import uuid
from cryptography.fernet import Fernet
from faststream import Depends, FastStream
from faststream.rabbit import RabbitBroker
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..config import SQLALCHEMY_DATABASE_URI
from queues.queues import  Queues, UploadDocument
from db.db import get_db_dependency
from ..models.document import Document
from ..document.adapter import GCPStorageAdapter


logger = logging.getLogger(__name__)

inject_session = get_db_dependency(SQLALCHEMY_DATABASE_URI)

def upload_document_flow(app: FastStream, broker: RabbitBroker):
    @broker.subscriber(Queues.UPLOAD_DOCUMENT.value)
    async def handle_document_creation(msg:UploadDocument, session: AsyncSession = Depends(inject_session)):
        logger.info(f"Received document creation event: {msg}")
        adapter = GCPStorageAdapter()
        document_info = msg

        document = Document(
            id = document_info.id,
            filename = document_info.filename,
            content_type = document_info.content_type,
            size = document_info.size,
            md5_hash = document_info.md5_hash,
            gcs_path = str(uuid.uuid4())
        )
        session.add(document)
        await session.commit()
        
        url=adapter.generate_presigned_put_url("1aca_va_la_cedula1",expiration=datetime.timedelta(minutes=5))
       
        return {
            "url": url
        }
    
async def list_all_documents(session: AsyncSession = Depends(inject_session)):
    
    result = await session.execute(select(Document))
    documents = result.scalars().all()  
    return documents

async def get_document_by_id(session: AsyncSession, document_id: uuid.UUID) -> Document:
    
    result = await session.execute(select(Document).where(Document.id == document_id))
    document = result.scalar_one_or_none()
    return document

#Endpoint para :Falta el flujo para mostrar un archivo (Listar todos los archivos de base de datos)
#Otro que por el id del archivo devuelve un url de vista temporal (30 min)