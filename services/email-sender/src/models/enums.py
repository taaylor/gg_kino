from enum import StrEnum


class EventType(StrEnum):
    TEST = "TEST"
    USER_REVIEW_LIKED = "USER_REVIEW_LIKED"
    USER_REGISTERED = "USER_REGISTERED"
    AUTO_MASS_NOTIFY = "AUTO_MASS_NOTIFY"
    MANAGER_MASS_NOTIFY = "MANAGER_MASS_NOTIFY"


class Priority(StrEnum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
