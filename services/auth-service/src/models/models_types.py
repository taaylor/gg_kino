from enum import StrEnum


class GenderEnum(StrEnum):
    MALE = "мужчина"
    FEMALE = "женщина"


class PermissionEnum(StrEnum):
    CRUD_ROLE = "CRUD_ROLE"
    ASSIGN_ROLE = "ASSIGN_ROLE"
    FREE_FILMS = "FREE_FILMS"
    PAID_FILMS = "PAID_FILMS"
