from enum import Enum, StrEnum


class SortedEnum(Enum):
    CREATED_ASC = "+created_at"
    CREATED_DESC = "-created_at"


class LikeEnum(Enum):
    LIKE = "like"
    DISLIKE = "dislike"


class FilmBookmarkState(StrEnum):
    """Состояния закладки фильма."""

    NOTWATCHED = "NOTWATCHED"
    WATCHED = "WATCHED"
