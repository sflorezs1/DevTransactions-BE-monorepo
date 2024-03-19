from typing import Annotated, List
from fastapi import FastAPI, Depends, HTTPException
from fastapi.concurrency import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from src.database import get_db_session, sessionmanager
from src.schemas import DocumentBase, DocumentCreate
import src.document.document_service as document_crud

import src.models

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Function that handles startup and shutdown events.
    To understand more, read https://fastapi.tiangolo.com/advanced/events/
    """
    yield
    if sessionmanager._engine is not None:
        # Close the DB connection
        await sessionmanager.close()

app = FastAPI(lifespan=lifespan)

@app.post("/documents/", response_model=DocumentBase)
async def create_document(document_data: DocumentCreate, db: AsyncSession = Depends(get_db_session)):
    return await document_crud.create(document_data, db)

@app.get("/documents/", response_model=List[DocumentBase])
async def get_all_documents(db: AsyncSession = Depends(get_db_session)):
    return await document_crud.get_all(db)

@app.get("/documents/{document_id}", response_model=DocumentBase)
async def get_document(document_id: str, db: AsyncSession = Depends(get_db_session)):
    document = await document_crud.get(document_id, db)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return document

@app.put("/documents/{document_id}", response_model=DocumentBase)
async def update_document(document_id: str, update_data: DocumentCreate, db: AsyncSession = Depends(get_db_session)):
    return await document_crud.update(document_id, update_data, db)

@app.delete("/documents/{document_id}")
async def delete_document(document_id: str, db: AsyncSession = Depends(get_db_session)):
    await document_crud.delete(document_id, db)
    return {"message": "Document deleted successfully"} 