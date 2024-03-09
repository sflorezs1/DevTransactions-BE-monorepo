from enum import Enum, auto

from microservices import MicroserviceEnum


class MessageQueues:
    class User:
        CREATE_ACCOUNT_QUEUE = 'user_create_account', MicroserviceEnum.USER
        UPDATE_PROFILE_QUEUE = 'user_update_profile', MicroserviceEnum.USER
        # ... add more User queues

    class Document:
        UPLOAD_DOCUMENT_QUEUE = 'document_upload', MicroserviceEnum.DOCUMENT
        PROCESS_DOCUMENT_QUEUE = 'document_process', MicroserviceEnum.DOCUMENT
        # ... add more Document queues

    class Request:
        SUBMIT_REQUEST_QUEUE = 'request_submit', MicroserviceEnum.REQUEST
        # ... add more Request queues

    class Audit:
        LOG_EVENT_QUEUE = 'audit_log_event', MicroserviceEnum.AUDIT
        # ... add more Audit queues

    # Add queues for the bridges
    class UserBridge:
        # ... queues used for User bridge communication
        pass

    class DocumentBridge:
        # ...
        pass

    class RequestBridge:
        # ...
        pass

    class AuditBridge:
        # ...
        pass
