from enum import Enum
import pika
import json
from typing import Any, Callable


from enum import Enum
import pika
import json
from typing import Any, Callable
from .queues import MessageQueues


def get_rabbitmq_connection(
    host: str = 'localhost', 
    port: int = 5672, 
    credentials: tuple[str, str] | None = None
) -> pika.BlockingConnection:
    """Establish a connection to a RabbitMQ server."""
    if credentials: 
        credentials = pika.PlainCredentials(*credentials)
    else:
        credentials = None

    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=host, port=port, credentials=credentials)
    )
    return connection


class RabbitMQUtils:
    def __init__(self, host: str ='localhost', port: int = 5672, credentials: tuple[str, str] | None = None):
        self._connection = get_rabbitmq_connection(host, port, credentials)
        self._channel = self._connection.channel()

    def produce_message(
        self, 
        queue_enum: MessageQueues, 
        message: dict, 
        exchange: str = '', 
        routing_key: str | None =None
    ) -> None:
        """Publish a message to a RabbitMQ queue based on the provided enum value."""
        message = json.dumps(message)
        if not routing_key:
            routing_key = queue_enum.value 
        self.channel.basic_publish(exchange=exchange, routing_key=routing_key, body=message)

    def consume_messages(
        self, 
        queue_enum: MessageQueues, 
        callback: Callable[[pika.channel.Channel, pika.spec.Basic.Deliver, pika.spec.BasicProperties, bytes], None]
    ) -> None:
        """Consume messages from a RabbitMQ queue based on the provided enum value."""
        self.channel.queue_declare(queue=queue_enum.value)
        self.channel.basic_consume(queue=queue_enum.value, auto_ack=True, on_message_callback=callback)
        self.channel.start_consuming()

    @property  
    def channel(self) -> pika.Channel:
        return self._channel

    def close(self) -> None:
        self._connection.close()
