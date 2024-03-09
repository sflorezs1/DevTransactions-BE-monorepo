from enum import Enum, auto

class MicroserviceEnum(Enum):
    USER = auto()
    DOCUMENT = auto()
    REQUEST = auto()
    AUDIT = auto()


class MicroserviceBridgeEnum(Enum):
    USER_BRIDGE = auto()
    DOCUMENT_BRIDGE = auto()
    REQUEST_BRIDGE = auto()
    AUDIT_BRIDGE = auto()