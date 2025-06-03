from enum import StrEnum


class EventTypes(StrEnum):
    LIKE = "like"
    COMMENT = "comment"
    WATCH_PROGRESS = "watch_progress"
    WATCH_LIST = "watch_list"
