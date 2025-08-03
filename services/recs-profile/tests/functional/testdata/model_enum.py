from enum import StrEnum


class GenderEnum(StrEnum):
    MALE = "MALE"
    FEMALE = "FEMALE"


class RecsSourceType(StrEnum):
    HIGH_RATING = "HIGH_RATING"
    ADD_BOOKMARKS = "ADD_BOOKMARKS"
