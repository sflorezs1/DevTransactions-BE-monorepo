from pydantic import BaseModel, EmailStr
from dataclasses import  dataclass
import uuid 

@dataclass
class UserCreate(BaseModel):
    id: uuid.UUID 
    name: str 
    email: EmailStr
    cedula: int
    address: str  
    operatorId: str
    operatorName: str