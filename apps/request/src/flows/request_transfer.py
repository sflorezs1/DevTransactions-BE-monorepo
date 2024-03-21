import logging
from os import name
from cryptography.fernet import Fernet
from faststream import Depends, FastStream
from faststream.rabbit import RabbitBroker
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from notification.notification import send_template_email
from ..models import StateEnum, User
from auth.auth import create_user
from ..config import FERNET_CRYPTO_KEY, FRONT_END_URL, OPERATOR_ID, OPERATOR_NAME, SQLALCHEMY_DATABASE_URI
from queues.queues import CentralizerRequest, CentralizerRequestType, CentralizerResponse, CompleteRegister, Queues, RegisterUser
from db.db import get_db_dependency

logger = logging.getLogger(__name__)

inject_session = get_db_dependency(SQLALCHEMY_DATABASE_URI)



def transfer_request_flow(app: FastStream, broker: RabbitBroker):
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
    
    