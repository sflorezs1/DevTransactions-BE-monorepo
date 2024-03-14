from pydantic import BaseModel  , EmailStr
class Operador(BaseModel):
    name: str
    address: str
    contactMail: EmailStr
    participants: list[str] 
