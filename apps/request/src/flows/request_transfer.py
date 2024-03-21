from ast import parse
import email
import json
import logging
from os import name
from webbrowser import Opera
from auth.api_dependency import ContextAuth
from cryptography.fernet import Fernet
from faststream import Depends, FastStream
from faststream.rabbit import RabbitBroker
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from notification.notification import send_template_email
from ..models import StateEnum, User
from auth.auth import create_user
from ..config import FERNET_CRYPTO_KEY, FRONT_END_URL, OPERATOR_ID, OPERATOR_NAME, SQLALCHEMY_DATABASE_URI
from queues.queues import CentralizerRequest, CentralizerRequestType, OperatorInfo, Queues, TransferRequestPayload, TransferUserPayload
from db.db import get_db_dependency

logger = logging.getLogger(__name__)

inject_session = get_db_dependency(SQLALCHEMY_DATABASE_URI)

def transfer_request_flow(app: FastStream, broker: RabbitBroker):
    @broker.subscriber(Queues.START_USER_TRANSFER.value)
    async def handle_user_transfer(request: TransferRequestPayload, auth: ContextAuth, session: AsyncSession = Depends(inject_session)):
        logger.info(f"Received user transfer event: {request}")

        transfer_payload: TransferUserPayload = TransferUserPayload(email=auth.email)
        operator_info: OperatorInfo = OperatorInfo(operator_id=request.operator_id) 

        async with broker:
            get_operators_payload = CentralizerRequest(
                type=CentralizerRequestType.GET_OPERATORS,
                payload=None,
            )
            operators = await broker.publish(get_operators_payload, Queues.GET_OPERATORS.value, rpc=True)
            parsed_operators = [ OperatorInfo(
                    operator_id=op["_id"], 
                    operator_name=op["operatorName"], 
                    operator_transfer_url=op["transferAPIURL"]
                ) for op in operators.message ]
            selected_operator = next(filter(lambda op: op.operator_id == request.operator_id, parsed_operators), None)
            if not selected_operator or not selected_operator.operator_transfer_url:
                send_template_email('User', auth.email, 'neqvygmj8mwg0p7w', {})
                return {
                    "message": "Operator or transfer url not found.",
                }

            operator_info.operator_name = selected_operator.operator_name
            operator_info.operator_transfer_url = selected_operator.operator_transfer_url

            await broker.publish([transfer_payload, operator_info], Queues.ADD_USER_TRANSFER_INFO.value)

        return {
            "message": "User transfer started successfully",
        }
    
    @broker.subscriber(Queues.COMPLETE_USER_TRANSFER.value)
    async def handle_user_transfer(request: TransferRequestPayload, auth: ContextAuth, session: AsyncSession = Depends(inject_session)):
        logger.info(f"Received user transfer event: {request}")

        transfer_payload: TransferUserPayload = TransferUserPayload(email=auth.email)
        operator_info: OperatorInfo = OperatorInfo(operator_id=request.operator_id) 

        async with broker:
            await broker.publish([transfer_payload, operator_info], Queues.ADD_USER_TRANSFER_INFO.value)

        return {
            "message": "User transfer started successfully",
        }