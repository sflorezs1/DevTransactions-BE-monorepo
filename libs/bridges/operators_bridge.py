import pika
import requests
import json
from fastapi import FastAPI
from schema.other_operators import GetOperatorsItem
from ms_tools.src.communication import MessageQueues, RabbitMQUtils
from ms_tools.src.events import Event

GOVCARPETA_API_URL = 'https://govcarpeta-21868b7e9dd3.herokuapp.com/apis/getOperators'
RABBITMQ_HOST = 'localhost'
RABBITMQ_PORT = 5672
QUEUE_NAME = 'get_operators'

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host=RABBITMQ_HOST, port=RABBITMQ_PORT))
channel = connection.channel()
channel.queue_declare(queue=QUEUE_NAME)

rmq_utils = RabbitMQUtils()

def process_operator_data():
    """Fetches operator data from the API and sends it to RabbitMQ."""
    response = requests.get(GOVCARPETA_API_URL)
    if response.status_code == 200:
        operators_data = response.json()
        for operator in operators_data:
            message = json.dumps(operator)
            event = Event(queue=MessageQueues.User.CREATE_ACCOUNT_QUEUE, body=message)
            rmq_utils.produce_message(MessageQueues.User.CREATE_ACCOUNT_QUEUE, event.__dict__) 
            channel.basic_publish(exchange='', routing_key=QUEUE_NAME, body=message)
    else:
        print(f"Error getting operator data: {response.status_code}")

app = FastAPI()

@app.get("/get_operators", response_model=GetOperatorsItem)
def get_operators():
    process_operator_data()  
    return []
