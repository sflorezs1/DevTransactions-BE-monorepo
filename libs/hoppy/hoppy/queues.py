from enum import Enum


class Queues(Enum):
    # User -> register
    START_USER_REGISTER = 'user.start_user_register' 
    PROCESS_USER_VALIADATION = 'user.process_user_validation' 
    DECLINE_USER_REGISTER = 'user.decline_user_register'
    REGISTER_IN_CENTRALIZER = 'user.register_in_centralizer'
    COMPLETE_USER_REGISTER = 'user.complete_user_register'
    CREATE_USER_PASSWORD = 'user.create_user_password'

    # User -> transfer
    TRANSFER_USER = 'user.transfer_user'

    # Centralizer -> register
    REQUESTS_QUEUE = 'centralizer.requests'

    #
    DOCUMENTS_QUEUE = 'documents.document_info'