from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import hashlib

from src.models import Document
from src.schemas import DocumentBase, DocumentCreate  # Import your models

async def get( document_id: str, db: AsyncSession) -> DocumentBase:
    query = select(Document).where(Document.id == document_id)
    result = await db.execute(query)
    return result.scalars().first()  

async def get_all(db: AsyncSession) -> List[DocumentBase]:
    query = select(Document)
    result = await db.execute(query)
    return result.scalars().all()


async def create(file_data: DocumentCreate, db: AsyncSession) -> DocumentBase:
    # Calculate MD5 hash (assuming you have the file contents)
    file_contents = bytes(128)
    md5_hash = hashlib.md5(file_contents).hexdigest() 

    # Create the Document object
    document = Document(
        filename=file_data.filename,
        content_type=file_data.content_type,
        size=file_data.size,
        gcs_path=file_data.gcs_path,
        md5_hash=md5_hash
    )  
    db.add(document)
    await db.commit() 
    await db.refresh(document)  
    return document 


async def update(document_id: str, update_data: DocumentCreate, db: AsyncSession) -> DocumentBase:
    file = await get(document_id)
    for key, value in update_data.dict(exclude_unset=True).items():
        setattr(file, key, value)  
    db.add(file)
    await db.commit()
    await db.refresh(file) 
    return file 

async def delete(document_id: str, db: AsyncSession) -> None:
    file = await get(document_id)
    await db.delete(file)
    await db.commit()  
