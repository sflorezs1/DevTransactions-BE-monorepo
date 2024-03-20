from secret.secrets import access_secret_version


DEBUG = True

# RabbitMQ configuration
RABBITMQ_HOST = access_secret_version('rabbitmq-host', 'localhost')
RABBITMQ_PORT = int(access_secret_version('rabbitmq-port', '5672'))
RABBITMQ_USER = access_secret_version('rabbitmq-user', 'localhost')
RABBITMQ_PASS = int(access_secret_version('rabbitmq-pass', '5672'))
RABBITMQ_URL = f"amqp://{RABBITMQ_USER}:{RABBITMQ_PASS}@{RABBITMQ_HOST}:{RABBITMQ_PORT}"

