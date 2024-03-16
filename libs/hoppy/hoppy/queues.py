from enum import Enum


class Queues(Enum):
    # User -> register
    START_USER_REGISTER = 'user.start_user_register'  # request
    DECLINE_USER_REGISTER = 'user.decline_user_register'  # response
    REGISTER_USER = 'user.register_user'  # response
    COMPLETE_USER_REGISTER = 'user.complete_user_register'  # request

    # User -> transfer
    TRANSFER_USER = 'user.transfer_user'

    # Centralizer -> register
    REQUESTS_QUEUE = 'centralizer.requests'