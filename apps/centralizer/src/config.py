# RabbitMQ configuration
# RabbitMQ configuration
from secret.secrets import access_secret_version

DEBUG = True
MOCK_CENTRALIZER = access_secret_version('mock-centralizer').replace('\n', '') == 'True'

RABBITMQ_HOST = access_secret_version('rabbitmq-host', 'localhost')
RABBITMQ_PORT = int(access_secret_version('rabbitmq-port', '5672'))
RABBITMQ_USER = access_secret_version('rabbitmq-user', None)
RABBITMQ_PASS = access_secret_version('rabbitmq-pass', None)
RABBITMQ_URL = f"amqp://{RABBITMQ_USER}:{RABBITMQ_PASS}@{RABBITMQ_HOST}:{RABBITMQ_PORT}" if RABBITMQ_USER else f"amqp://{RABBITMQ_HOST}:{RABBITMQ_PORT}"

CENTRALIZER_BASE_URL = access_secret_version('centralizer-base-url', 'https://govcarpeta-21868b7e9dd3.herokuapp.com')
