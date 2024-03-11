import pika
import requests
import json
from fastapi import FastAPI

RABBITMQ_HOST = 'localhost'
RABBITMQ_PORT = 5672
QUEUE_NAME = 'get_operators'

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host=RABBITMQ_HOST, port=RABBITMQ_PORT))
channel = connection.channel()
channel.queue_declare(queue=QUEUE_NAME)


def process_operator_data():
    """Fetches operator data from the API and sends it to RabbitMQ."""
    response = requests.get("https://govcarpeta.../apis/getOperators")
    if response.status_code == 200:
        operators_data = response.json()
        for operator in operators_data:
            message = json.dumps(operator)
            channel.basic_publish(exchange='', routing_key=QUEUE_NAME, body=message)
    else:
        print(f"Error getting operator data: {response.status_code}")

app = FastAPI()

@app.get("/update_operators")
def update_operators():
    """Endpoint to trigger operator data update and send to RabbitMQ."""
    try:
        process_operator_data()
        return {"status": "success", "message": "Operator data sent to queue"}
    except Exception as e:
        return {"status": "error", "message": f"Error updating operators: {e}"}


# How to trigger the bridge (replace with your implementation)
# Option 1: Call process_operator_data from a FastAPI endpoint
# Option 2: Use a scheduler to call process_operator_data periodically
