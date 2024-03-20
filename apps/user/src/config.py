from secret import access_secret_version

DEBUG = True

# RabbitMQ configuration
RABBITMQ_HOST = access_secret_version('rabbitmq-host', 'localhost')
RABBITMQ_PORT = int(access_secret_version('rabbitmq-port', '5672'))
RABBITMQ_USER = access_secret_version('rabbitmq-user', 'localhost')
RABBITMQ_PASS = access_secret_version('rabbitmq-pass')
RABBITMQ_URL = f"amqp://{RABBITMQ_USER}:{RABBITMQ_PASS}@{RABBITMQ_HOST}:{RABBITMQ_PORT}"

# SQLAlchemy configuration
SQLALCHEMY_USERNAME = access_secret_version('sqlalchemy-username', 'postgres')
SQLALCHEMY_PASSWORD = access_secret_version('sqlalchemy-password', 'postgres')
SQLALCHEMY_HOST = access_secret_version('sqlalchemy-host', 'localhost')
SQLALCHEMY_PORT = int(access_secret_version('sqlalchemy-port', '5432'))
SQLALCHEMY_DATABASE = 'dt_user'

SQLALCHEMY_DATABASE_URI = f"postgresql+asyncpg://{SQLALCHEMY_USERNAME}:{SQLALCHEMY_PASSWORD}@{SQLALCHEMY_HOST}:{SQLALCHEMY_PORT}/{SQLALCHEMY_DATABASE}"

FERNET_CRYPTO_KEY = access_secret_version('fernet-crypto-key')
FRONT_END_URL = access_secret_version('front-end-url', 'http://localhost:3000')

OPERATOR_ID = access_secret_version('operator-id')
OPERATOR_NAME = access_secret_version('operator-name')