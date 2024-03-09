from abc import ABC, abstractmethod
from datetime import timedelta

class CloudStorageAdapter(ABC):
    @abstractmethod
    def upload_file(self, bucket_name: str, source_file_path: str, destination_blob_name: str) -> None:
        pass

    @abstractmethod
    def download_file(self, bucket_name: str, source_blob_name: str, destination_file_path: str) -> None:
        pass

    @abstractmethod
    def list_blobs(self, bucket_name: str, prefix: str = None) -> list[str]:
        pass

    @abstractmethod
    def delete_blob(self, bucket_name: str, blob_name: str) -> None:
        pass

    @abstractmethod
    def generate_presigned_get_url(self, bucket_name: str, blob_name: str, expiration: timedelta) -> str:
        pass

    @abstractmethod
    def generate_presigned_put_url(self, bucket_name: str, blob_name: str, expiration: timedelta, expected_md5: str = None) -> str:
        pass