import base64
import json
import logging
import urllib.parse
from faststream import Depends, FastStream
from faststream.rabbit import RabbitBroker
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from notification.notification import send_template_email
from ..models.user import StateEnum, User
from auth.auth import create_user
from ..config import FERNET_CRYPTO_KEY, FRONT_END_URL, OPERATOR_ID, OPERATOR_NAME, SQLALCHEMY_DATABASE_URI
from queues.queues import CentralizerRequest, CentralizerRequestType, CentralizerResponse, CompleteRegister, Queues, RegisterUser
from db.db import get_db_dependency

logger = logging.getLogger(__name__)

inject_session = get_db_dependency(SQLALCHEMY_DATABASE_URI)


def send_declination_email(user_data):
    """
    Sends a declination email to the user.

    Args:
        user_data (RegisterUserPayload): The user data containing the email and name.

    Returns:
        None
    """
    send_template_email(
        to_name=user_data.name,
        to_email=user_data.email, 
        template_id='ynrw7gy12drg2k8e', 
        template_data={
            "name": user_data.name,
        },
        subject="Registro declinado"
    )

def generate_complete_register_link(user_data) -> str:
    """
    Generates a complete registration link with encrypted user data.

    Args:
        user_data (RegisterUserPayload): The user data to be included in the link.

    Returns:
        str: The complete registration link with encrypted user data.
    """
    params_dict = {
        "name": user_data.name,
        "email": user_data.email,
        "national_id": user_data.national_id,
    }

    # Convert the dictionary to a JSON string
    params_json = json.dumps(params_dict)

    # Encode the JSON string as a base64 string
    params_base64 = base64.b64encode(params_json.encode()).decode()

    params_string = urllib.parse.urlencode({
        "params": params_base64,
    })
    return f"{FRONT_END_URL}?params={urllib.parse.quote_plus(params_string)}"

def user_registration_flow(app: FastStream, broker: RabbitBroker):
    @broker.subscriber(Queues.START_USER_REGISTER.value)
    async def handle_user_creation(msg: RegisterUser, session: AsyncSession = Depends(inject_session)):
        """
        Handle user creation event.

        Args:
            event (Event): The event object containing the user creation data.
            context (Context): The context object for the event.

        Returns:
            None
        """
        logger.info(f"Received user creation event: {msg}")
        user_data = msg

        user = User(
            name = user_data.name,
            email = user_data.email,
            national_id = user_data.national_id,
            address = user_data.address,
            state = StateEnum.INACTIVE.value,
        )
        session.add(user)
        await session.commit()

        logger.info(f"Successfully created user: {user}")
        logger.info("Validating user in centralizer")

        validate_citizen_payload = CentralizerRequest(
            type = CentralizerRequestType.VALIDATE_CITIZEN,
            payload = {
                "email": user_data.email,
                "id": user_data.national_id,
            },
            reply_to = Queues.PROCESS_USER_VALIADATION.value
        )

        await broker.publish(validate_citizen_payload, Queues.REQUESTS_QUEUE.value)

        logger.info(f"Sending response to requestor {msg.reply_to}")

        return {
            "message": "User creation event received"
        }
    
    @broker.subscriber(Queues.PROCESS_USER_VALIADATION.value)
    async def handle_user_validation(msg: CentralizerResponse, session: AsyncSession = Depends(inject_session)):
        """
        Handle user validation message received from the broker.

        Args:
            msg: The message received from the broker.
            session: The database session.

        Raises:
            Exception: If the user is not found.

        Returns:
            None
        """
        logger.info(f"Centralizer response: {msg}")
        user = (await session.execute(select(User).filter_by(email=msg.original_payload["email"]))).scalars().first()

        if not user:
            raise Exception("User not found")

        match msg.status:
            case 204: 
                # User is not registered
                register_citizen_payload = CentralizerRequest(
                    type=CentralizerRequestType.REGISTER_CITIZEN,
                    payload={
                        "id": user.national_id,
                        "name": user.name,
                        "email": user.email,
                        "address": user.address,
                        "operator_id": OPERATOR_ID,
                        "operator_name": OPERATOR_NAME,
                    },
                    reply_to=Queues.COMPLETE_USER_REGISTER.value
                )
                await broker.publish(register_citizen_payload, Queues.REQUESTS_QUEUE.value)
            case _:
                send_declination_email(user)
                await session.delete(user)

    # User may be registered
    @broker.subscriber(Queues.COMPLETE_USER_REGISTER.value)
    async def handle_complete_user_registration(msg: CentralizerResponse, session: AsyncSession = Depends(inject_session)):
        """
        Handle the complete user registration message.

        Args:
            msg (dict): The message containing the registration status and payload.
            session (AsyncSession, optional): The database session. Defaults to Depends(inject_session).

        Returns:
            None
        """

        user = (await session.execute(select(User).filter_by(email=msg.original_payload["email"]))).scalars().first()

        if not user:
            raise Exception("User not found")

        if msg.status != 201:
            send_declination_email(user)
            return
        
        send_template_email(
            to_name=user.name,
            to_email=user.email, 
            template_id='vywj2lpj2w1l7oqz', 
            template_data={
                "name": user.name,
                "complete_register_link": generate_complete_register_link(user) 
            },
            subject="Completa tu registro"
        )

    @broker.subscriber(Queues.CREATE_USER_PASSWORD.value)
    async def handle_create_user_password(msg, session: AsyncSession = Depends(inject_session)):
        user = await session.query(User).filter_by(email=msg.email).first()

        if not user:
            return
        
        create_user(user.email, user.password)

        user.state = StateEnum.ACTIVE.value

        session.add(user)
        await session.commit()

        await app.send_message(msg.reply_to, {
            "message": "User password created successfully"
        })
    
def crud_user(app: FastStream, broker: RabbitBroker):
    @broker.subscriber(Queues.GET_USER.value)
    async def handle_get_user(email: str, session: AsyncSession = Depends(inject_session)):
        user = (await session.execute(select(User).filter_by(email=email))).scalar_one_or_none()

        if user:
            return {
                "user": {
                    "name": user.name,
                    "email": user.email,
                    "national_id": user.national_id,
                    "address": user.address,
                }
            }
        else:
            return None
