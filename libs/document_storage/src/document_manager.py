from datetime import timedelta
from google.cloud import storage

from .adapter import CloudStorageAdapter


class GCPStorageAdapter(CloudStorageAdapter):
    def __init__(self, project_id: str):
        self._client = storage.Client(project=project_id)

    def upload_file(self, bucket_name: str, source_file_path: str, destination_blob_name: str) -> None:
        """Uploads a file to a GCS bucket."""
        bucket = self._client.bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)
        blob.upload_from_filename(source_file_path)

    def download_file(self, bucket_name: str, source_blob_name: str, destination_file_path: str) -> None:
        """Downloads a file from a GCS bucket."""
        bucket = self._client.bucket(bucket_name)
        blob = bucket.blob(source_blob_name)
        blob.download_to_filename(destination_file_path)

    def list_blobs(self, bucket_name: str, prefix: str = None) -> list[str]:
        """Lists blobs in a GCS bucket, optionally filtered by a prefix."""
        bucket = self._client.bucket(bucket_name)
        blobs = bucket.list_blobs(prefix=prefix)
        return [blob.name for blob in blobs]

    def delete_blob(self, bucket_name: str, blob_name: str) -> None:
        """Deletes a blob from a GCS bucket."""
        bucket = self._client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        blob.delete()

    def generate_presigned_get_url(self, bucket_name: str, blob_name: str, expiration: timedelta) -> str:
        bucket = self._client.bucket(bucket_name)
        blob = bucket.blob(blob_name)

        url = blob.generate_signed_url(
            version="v4",
            expiration=expiration,
            method="GET"
        )
        return url

    def generate_presigned_put_url(self, bucket_name: str, blob_name: str, expiration: timedelta, expected_md5: str = None) -> str:
        bucket = self._client.bucket(bucket_name)
        blob = bucket.blob(blob_name)

        conditions = []
        if expected_md5:
            conditions.append(['content-md5', expected_md5])

        url = blob.generate_signed_url(
            version="v4",
            expiration=expiration,
            method="PUT",
            content_md5=expected_md5,  # Optional
            conditions=conditions 
        )
        return url
