import pika
import json
import time
import uuid
from fastapi import FastAPI, HTTPException, Depends, Body
from typing import Optional


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
    

def process_user_registration(message: dict) -> bool:
# Replace this with the actual logic to register a user in your 'user' microservice
# For now, let's simulate successful registration
    print(f"Received registration request: {message}")
    time.sleep(2)  # Simulate processing delay
    return True


# RPC Call with Registration Logic
def rpc_call(ch: pika.channel.Channel, message: str) -> Optional[str]:
    # ... (Same as before) 

    ch.basic_publish(
        exchange='',
        routing_key=QUEUE_NAME,
        properties=pika.BasicProperties(
            reply_to=RABBITMQ_QUEUE,
            correlation_id=corr_id
        ),
        body=message
    )

    # ... (Waiting for response logic)

    # Assuming the consumer sends back a simple success message
    return result


# FastAPI Endpoint
@app.post("/user/register")
async def register_user(user_data: dict, channel: pika.channel.Channel = Depends(get_channel)):
    try:
        response = rpc_call(channel, json.dumps(user_data))
        if response == 'success':
            return {"message": "User registration successful"}
        else:
            raise HTTPException(status_code=500, detail="User registration failed")
    except TimeoutError:
        raise HTTPException(status_code=504, detail="Request timed out")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 
    

import pika
import json
import requests # For interacting with GovCarpeta
from fastapi import FastAPI, HTTPException, Body, Depends

from communication import MessageQueues, RabbitMQUtils  

# ... RabbitMQ Configuration values ... 

app = FastAPI()
rmq_utils = RabbitMQUtils()  # Create a RabbitMQUtils instance

# ... GovCarpeta Interaction Logic ...  

@app.post("/user/register")  
async def register_user(user_data: dict):
    try:
        # Check with GovCarpeta (unchanged from before)
        govcarpeta_response = requests.post(f"{GOVCARPETA_BASE_URL}/users/{user['id']}")
        # ... handle GovCarpeta response ...

        # Send user data to the User Microservice 
        event = Event(queue=MessageQueues.User.CREATE_ACCOUNT_QUEUE, body=user_data)
        rmq_utils.produce_message(MessageQueues.User.CREATE_ACCOUNT_QUEUE, event.__dict__) 

        # RPC Handling - you'll need to fill this logic based on your RPC implementation
        response = await rpc_call_for_user_registration()  # Assuming you have a function for this
        if response == 'success':
            return {"message": "User registration in progress"}  # Or suitable message 
        else:
            raise HTTPException(status_code=500, detail="User registration failed")

    except Exception as e:  # Consider more refined error handling
        raise HTTPException(status_code=500, detail=str(e)) 
