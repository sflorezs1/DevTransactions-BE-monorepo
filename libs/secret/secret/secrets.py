import os
from google.cloud import secretmanager
from .config import PROJECT_ID

def access_secret_version(secret_id: str, default_value: str = None, version_id: str = 'latest'):
    env = os.getenv('ENV', 'dev')
    if env != 'prod' and default_value is not None:
        return default_value

    client = secretmanager.SecretManagerServiceClient()
    name = client.secret_version_path(project=PROJECT_ID, secret=secret_id, secret_version=version_id)
    response = client.access_secret_version(name=name)
    return response.payload.data.decode('UTF-8').replace('\n','')
