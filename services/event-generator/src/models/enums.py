from enum import StrEnum


class NotificationMethod(StrEnum):
    EMAIL = "EMAIL"
    WEBSOCKET = "WEBSOCKET"


class Priority(StrEnum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class EventType(StrEnum):
    MANAGER_MASS_NOTIFY = "MANAGER_MASS_NOTIFY"
