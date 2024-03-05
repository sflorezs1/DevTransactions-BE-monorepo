from pydantic import BaseModel, Field, HttpUrl, validator
from uuid import UUID

class DocumentBase(BaseModel):
    id: UUID = Field(..., description="Unique ID of the document.") 
    filename: str = Field(..., description="The original name of the file.")
    content_type: str = Field(None, description="The MIME type of the file.")
    size: int = Field(..., description="The file size in bytes.")
    gcs_path: str = Field(..., description="Google Cloud Storage object path.")
    gcs_key: str = Field(None, description="Optional key for specific GCS file access.")
    md5_hash: str = Field(None, description="MD5 hash of the file contents.")


class DocumentCreate(BaseModel):
    class Config:
        fields = {'id': {'exclude': True}}
        extra = 'forbid'

    filename: str = Field(..., description="The original name of the file.")
    content_type: str = Field(None, description="The MIME type of the file.")
    size: int = Field(..., description="The file size in bytes.")
    gcs_path: str = Field(..., description="Google Cloud Storage object path.")

    @validator('gcs_path')
    def validate_gcs_path(cls, value):
        if not value.startswith('gs://'):
            raise ValueError('GCS path must start with "gs://"')
        # Add more sophisticated validation logic here if needed
        return value
    

