from google.cloud import secretmanager

from enum import Enum
from .adapter import SecretsAdapter

class SecretNames(Enum):
    DATABASE_PASSWORD = 'db_password'
    API_KEY = 'my_api_key'
    STRIPE_SECRET_KEY = 'stripe_secret'
    # ... add more secret names as needed


class GCPSecretsManager(SecretsAdapter):
    def __init__(self, project_id: str):
        self._client = secretmanager.SecretManagerServiceClient()
        self._project_id = project_id

    def get_secret(self, secret_name: SecretNames, version_id: str = 'latest') -> str:
        """Retrieves the value of a secret from Google Secret Manager."""
        secret_id = secret_name.value  # Get the secret ID 
        name = f"projects/{self._project_id}/secrets/{secret_id}/versions/{version_id}"
        response = self._client.access_secret_version(request={"name": name})
        return response.payload.data.decode("UTF-8")
