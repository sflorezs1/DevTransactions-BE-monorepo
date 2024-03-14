from pydantic import BaseModel, EmailStr
class GetOperatorsItem(BaseModel):
    OperatorId: str
    OperatorName: str
    transferAPIURL: str