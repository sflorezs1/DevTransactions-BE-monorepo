import pika
import requests
import json
from fastapi import FastAPI, Body

RABBITMQ_HOST = 'local_host'
RABBITMQ_PORT = 5672
QUEUE_NAME = 'user_registrations'  

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host=RABBITMQ_HOST, port=RABBITMQ_PORT))
channel = connection.channel()
channel.queue_declare(queue=QUEUE_NAME)


def send_user_registration(user_data: dict): 

    message = json.dumps(user_data)
    channel.basic_publish(exchange='', routing_key=QUEUE_NAME, body=message)


app = FastAPI()


@app.post("/register_user")  
def register_user(user: dict = Body(...)):  
    """API endpoint to receive user data and send it to RabbitMQ."""
    try:
        send_user_registration(user) 
        return {"status": "success", "message": "User registration data sent to queue"}
    except Exception as e:
        print(f"Error sending user data: {e}")
        return {"status": "error", "message": "Error registering user"}
    

# GovCarpeta API details 
GOVCARPETA_BASE_URL = 'https://govcarpeta-21868b7e9dd3.herokuapp.com/'

def register_user(user: dict = Body(...)):
    
    govcarpeta_response = requests.get(f"{GOVCARPETA_BASE_URL}/users/{user['id']}")
    if govcarpeta_response.status_code == 200:
        # User exists in GovCarpeta
        return {"status": "warning", "message": "User already exists in GovCarpeta"}
    elif govcarpeta_response.status_code == 404:
        # User not found, proceed
        send_user_registration(user) 
        return {"status": "success", "message": "User registered"}
    else:
        # Handle unexpected GovCarpeta errors
        return {"status": "error", "message": f"Error checking user in GovCarpeta: {govcarpeta_response.status_code}"}