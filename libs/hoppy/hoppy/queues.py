from enum import Enum


class Queues(Enum):
    # User
    REGISTER_USER = 'user.register_user'
    TRANSFER_USER = 'user.transfer_user'

    # Centralizer
    REGISTER_CITIZEN = 'centralizer.register_citizen'