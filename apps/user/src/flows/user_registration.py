import logging
from os import name
from cryptography.fernet import Fernet
import urllib.parse
from notification.notification import send_template_email

from ..models.user import StateEnum, User
from ..services.firebase_auth import create_user
from ..config import FERNET_CRYPTO_KEY, FRONT_END_URL, OPERATOR_ID, OPERATOR_NAME
from hoppy.event import CentralizerResponsePayload, CreatePasswordPayload, Event, RegisterUserPayload
from hoppy.hoppy import Context, Hoppy
from hoppy.queues import Queues

logger = logging.getLogger(__name__)

def generate_complete_register_link(user_data: RegisterUserPayload) -> str:
    cipher_suite = Fernet(FERNET_CRYPTO_KEY)
    params_string = urllib.parse.urlencode({
        "name": user_data.name,
        "email": user_data.email,
        "national_id": user_data.national_id,
    })
    encrypted_params = cipher_suite.encrypt(params_string.encode())
    return f"{FRONT_END_URL}?params={urllib.parse.quote_plus(encrypted_params)}"

def user_registration_flow(app: Hoppy):
    @app.consume(Queues.START_USER_REGISTER)
    async def handle_user_creation(event: Event, context: Context):
        user_data = event.body   # type: RegisterUserPayload

        user = User(
            name = user_data.name,
            email = user_data.email,
            national_id = user_data.national_id,
            address = user_data.address,
            state = StateEnum.INACTIVE.value,
        )
        context.session.add(user)
        await context.session.commit()

        validate_citizen_payload = {
            "type": "validate_citizen",
            "payload": user_data,
            "reply_to": Queues.PROCESS_USER_VALIADATION.value
        }
        await app.send_message(Queues.REQUESTS_QUEUE, validate_citizen_payload)

        await app.send_message(event.body.reply_to, {
            "message": "User creation event received"
        })

    @app.consume(Queues.PROCESS_USER_VALIADATION)
    async def handle_user_validation(event: Event, context: Context):
        response = event.body # type: CentralizerResponsePayload
        match response.status:
            case 204: # User is not registered
                app.send_message(Queues.REGISTER_IN_CENTRALIZER, response.original_payload)
            case _:
                app.send_message(Queues.DECLINE_USER_REGISTER, response.original_payload)

    # User is already registered
    @app.consume(Queues.DECLINE_USER_REGISTER)
    async def handle_decline_user_registration(event: Event, context: Context):
        user_data = event.body  # type: RegisterUserPayload
        await send_template_email(
            to_email=user_data.email, 
            template_id='ynrw7gy12drg2k8e', 
            data={
                "name": user_data.name,
            },
        )

    @app.consume(Queues.REGISTER_IN_CENTRALIZER)
    async def handle_register_in_centralizer(event: Event, context: Context):
        user_data = event.body

        validate_citizen_payload = {
            "type": "register_citizen",
            "payload": {
                "id": user_data.national_id,
                "name": user_data.name,
                "email": user_data.email,
                "address": user_data.address,
                "operator_id": OPERATOR_ID,
                "operator_name": OPERATOR_NAME,
            },
            "reply_to": Queues.COMPLETE_USER_REGISTER.value
        }
        await app.send_message(Queues.REQUESTS_QUEUE, validate_citizen_payload)

    
    # User may be registered
    @app.consume(Queues.COMPLETE_USER_REGISTER)
    async def handle_complete_user_registration(event: Event, context: Context):
        response = event.body # type: CentralizerResponsePayload

        if response.status != 201:
            app.send_message(Queues.DECLINE_USER_REGISTER, response.original_payload)
            return
        
        email = event.body.original_payload.email
        user = await context.session.query(User).filter_by(email=email).first()

        if not user:
            return

        await send_template_email(
            to_email=user.email, 
            template_id='vywj2lpj2w1l7oqz', 
            data={
                "name": user.name,
                "complete_register_link": generate_complete_register_link(user) 
            },
        )

    @app.consume(Queues.CREATE_USER_PASSWORD)
    async def handle_create_user_password(event: Event, context: Context):
        user_data = event.body  # type: CreatePasswordPayload
        user = await context.session.query(User).filter_by(email=user_data.email).first()

        if not user:
            return
        
        create_user(user_data.email, user_data.password)

        user.state = StateEnum.ACTIVE

        context.session.add(user)
        await context.session.commit()

        await app.send_message(event.body.reply_to, {
            "message": "User password created successfully"
        })
    