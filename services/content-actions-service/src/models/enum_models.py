from enum import Enum


class SortedEnum(Enum):
    CREATED_ASC = "+created_at"
    CREATED_DESC = "-created_at"


class LikeEnum(Enum):
    LIKE = "like"
    DISLIKE = "dislike"
