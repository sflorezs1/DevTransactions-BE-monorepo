from secret.secrets import access_secret_version


DEBUG = True

# RabbitMQ configuration
RABBITMQ_HOST = access_secret_version('rabbitmq-host', 'localhost')
RABBITMQ_PORT = int(access_secret_version('rabbitmq-port', '5672'))

