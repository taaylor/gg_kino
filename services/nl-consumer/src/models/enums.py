from enum import StrEnum


class ProcessingStatus(StrEnum):
    OK = "OK"
    INCORRECT_QUERY = "INCORRECT QUERY"
    FAILED = "FAILED"
