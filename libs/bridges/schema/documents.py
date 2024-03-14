from pydantic import BaseModel  
import uuid

class Document(BaseModel):
    idCitizen: int
    UrlDocument: str
    documentTitle: str
    documentType: str
    documentId: uuid.UUID 