import pika
import requests
from dataclasses import asdict
from fastapi import FastAPI, HTTPException, Path
from schema.user import UserCreate
from ms_tools.src.communication import MessageQueues, RabbitMQUtils
from ms_tools.src.events import Event

GOVCARPETA_API_URL = 'https://govcarpeta-21868b7e9dd3.herokuapp.com/apis/validateCitizen/{id}'
RABBITMQ_HOST = 'local_host'
RABBITMQ_PORT = 5672
QUEUE_NAME = 'user_registrations'  

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host=RABBITMQ_HOST, port=RABBITMQ_PORT))
channel = connection.channel()
channel.queue_declare(queue=QUEUE_NAME)

app = FastAPI()
rmq_utils = RabbitMQUtils()

def validate_citizen(citizen_id: int) -> bool:
    
    url = GOVCARPETA_API_URL.format(id=citizen_id) 
    response = requests.get(url)

    if response.status_code == 200:
        return True
    elif response.status_code == 204:
        return False
    else:
        return {"error": f"Error validating citizen: {response.status_code}"}

@app.get("/user/validateUser/{cedula}")
async def get_citizen(cedula: int = Path(..., title="Citizen ID", ge=1000000000)):
    
    is_registered = validate_citizen(cedula)

    if is_registered:
        return {"status": "registered"}
    else:
        return {"status": "not_registered"}

@app.post("/user/register")
async def register_user(user_data: UserCreate):

    try:
        if  validate_citizen(user_data.cedula) == True:
            raise HTTPException(
            status_code=409, 
            detail="Citizen already registered in another platform"
        )   
        else:    
            user_json = asdict(user_data)
            event = Event(queue=MessageQueues.User.CREATE_ACCOUNT_QUEUE, body=user_json)
            rmq_utils.produce_message(MessageQueues.User.CREATE_ACCOUNT_QUEUE, event.__dict__) 
        
    except TimeoutError:
        raise HTTPException(status_code=504, detail="Request timed out")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 
    