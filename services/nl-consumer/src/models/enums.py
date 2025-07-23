from enum import StrEnum


class HttpMethods(StrEnum):
    GET = "GET"
    POST = "POST"


class ProcessingStatus(StrEnum):
    OK = "OK"
    INCORRECT_QUERY = "INCORRECT QUERY"
    FAILED = "FAILED"
