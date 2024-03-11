import pika
import json
from fastapi import APIRouter  # ...or another web framework

# Configuration 
rabbitmq_host = 'your-rabbitmq-host'
rabbitmq_port = 5672  # Standard RabbitMQ port
queue_name = 'user_actions'  

# Initialize the router for API endpoints
router = APIRouter()  

# Establish RabbitMQ connection (ideally reuse a connection)
connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host, port=rabbitmq_port))
channel = connection.channel()
channel.queue_declare(queue=queue_name)

# Endpoint to receive user data from frontend
@router.post('/submit_user_data')
def submit_user(user_data: dict):  # Adjust the data type if needed
    try:
        message = json.dumps(user_data)
        channel.basic_publish(exchange='', routing_key=queue_name, body=message)
        return {'status': 'success'}
    except Exception as e:
        print(f"Error sending message: {e}")
        return {'status': 'error', 'message': str(e)}  
