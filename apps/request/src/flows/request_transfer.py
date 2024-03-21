from ast import parse
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
from ..config import SQLALCHEMY_DATABASE_URI
from queues.queues import CentralizerRequest, CentralizerRequestType, OperatorInfo, Queues, TransferFileCamelPayload, TransferRequestPayload, TransferUserCammelPayload, TransferUserPayload
from db.db import get_db_dependency
import aiohttp

logger = logging.getLogger(__name__)

inject_session = get_db_dependency(SQLALCHEMY_DATABASE_URI)

def transfer_decline_email(email):
    send_template_email('User', email, 'neqvygmj8mwg0p7w', {})


def transfer_request_flow(app: FastStream, broker: RabbitBroker):
    @broker.subscriber(Queues.START_USER_TRANSFER.value)
    async def handle_user_transfer(request: TransferRequestPayload, auth: ContextAuth, session: AsyncSession = Depends(inject_session)):
        logger.info(f"Received user transfer event: {request}")

        transfer_payload: TransferUserPayload = TransferUserPayload(email=auth.email, callback_url=f"http://backdt.ddns.com/request-bridge/request/complete_transfer")
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
                transfer_decline_email(auth.email)
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
    async def handle_user_transfer(requestransfer_payload: TransferUserPayload, operator_info: OperatorInfo, session: AsyncSession = Depends(inject_session)):
        cammelPayload = TransferUserCammelPayload(
            email=requestransfer_payload.email,
            callbackUrl=requestransfer_payload.callback_url,
            address=requestransfer_payload.address,
            id=requestransfer_payload.id,
            name=requestransfer_payload.name,
            files=[ TransferFileCamelPayload(
                documentTitle=file.document_title,
                urlDocument=file.url_document
            ) for file in requestransfer_payload.files ]
        )

        async with aiohttp.ClientSession() as session:
            async with session.post(operator_info.operator_transfer_url, json=cammelPayload) as response:
                if response.status == 200:
                    return {
                        "message": "User transfer started successfully",
                    }
                else:
                    transfer_decline_email(requestransfer_payload.email)
    