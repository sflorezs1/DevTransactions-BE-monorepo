from secret.secrets import access_secret_version


DEBUG = True

# RabbitMQ configuration
RABBITMQ_HOST = access_secret_version('rabbitmq-host', 'localhost')
RABBITMQ_PORT = int(access_secret_version('rabbitmq-port', '5672'))
RABBITMQ_USER = access_secret_version('rabbitmq-user', False)
RABBITMQ_PASS = access_secret_version('rabbitmq-pass', False)
RABBITMQ_URL = f"amqp://{RABBITMQ_USER}:{RABBITMQ_PASS}@{RABBITMQ_HOST}:{RABBITMQ_PORT}" if RABBITMQ_USER else f"amqp://{RABBITMQ_HOST}:{RABBITMQ_PORT}"

FRONT_END_URL = access_secret_version('front-end-url', 'http://localhost:3000')
