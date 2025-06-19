from enum import StrEnum


class GenderEnum(StrEnum):
    MALE = "MALE"
    FEMALE = "FEMALE"


class Methods(StrEnum):
    GET = "GET"
    PUT = "PUT"
    POST = "POST"
    DELETE = "DELETE"
