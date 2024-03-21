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
from queues.queues import CentralizerRequest, CentralizerRequestType, CentralizerResponse, CompleteRegister, OperatorInfo, Queues, RegisterUser, TransferUserPayload
from db.db import get_db_dependency

logger = logging.getLogger(__name__)

inject_session = get_db_dependency(SQLALCHEMY_DATABASE_URI)


def user_transfer_flow(app: FastStream, broker: RabbitBroker):
    @broker.subscriber(Queues.ADD_USER_TRANSFER_INFO.value)
    async def handle_user_transfer_info(transfer_payload: TransferUserPayload, operator_info: OperatorInfo, session: AsyncSession = Depends(inject_session)):
        logger.info(f"Received user transfer event: {transfer_payload}")

        user = (await session.execute(select(User).filter(User.email == transfer_payload.email))).scalar().first()

        if not user:
            raise Exception("User not found")
        
        transfer_payload.id = user.national_id
        transfer_payload.name = user.name
        transfer_payload.address = user.address

        async with broker:
            await broker.publish([transfer_payload, operator_info], Queues.ADD_USER_TRANSFER_DOCS_INFO.value)

        return {
            "message": "User creation event received"
        }
    