from datetime import timedelta
from google.cloud import storage
from ..config import BUCKET, PROJECT_ID
import logging


logger = logging.getLogger(__name__)

class GCPStorageAdapter():
    def __init__(self):
        
        self._client = storage.Client(project=PROJECT_ID)
        self.bucket = BUCKET
        logger.info(f"bucket = {self.bucket}")

    def upload_file(self, source_file_path: str, destination_blob_name: str) -> None:
        """Uploads a file to a GCS bucket."""
        bucket = self._client.bucket(self.bucket)
        blob = bucket.blob(destination_blob_name)
        blob.upload_from_filename(source_file_path)

    def download_file(self, source_blob_name: str, destination_file_path: str) -> None:
        """Downloads a file from a GCS bucket."""
        bucket = self._client.bucket(self.bucket)
        blob = bucket.blob(source_blob_name)
        blob.download_to_filename(destination_file_path)

    def list_blobs(self, prefix: str = None) -> list[str]:
        """Lists blobs in a GCS bucket, optionally filtered by a prefix."""
        bucket = self._client.bucket(self.bucket)
        blobs = bucket.list_blobs(prefix=prefix)
        return [blob.name for blob in blobs]

    def delete_blob(self, blob_name: str) -> None:
        """Deletes a blob from a GCS bucket."""
        bucket = self._client.bucket(self.bucket)
        blob = bucket.blob(blob_name)
        blob.delete()

    def generate_presigned_get_url(self, blob_name: str, expiration: timedelta) -> str:
        bucket = self._client.bucket(self.bucket)
        blob = bucket.blob(blob_name)

        url = blob.generate_signed_url(
            version="v4",
            expiration=expiration,
            method="GET"
        )
        return url

    def generate_presigned_put_url(self, blob_name: str, expiration: timedelta, expected_md5: str = None) -> str:
        bucket = self._client.bucket(self.bucket)
        blob = bucket.blob(blob_name)
        url = blob.generate_signed_url(
            version="v4",
            expiration=expiration,
            method="PUT",
        )
        return url
    

