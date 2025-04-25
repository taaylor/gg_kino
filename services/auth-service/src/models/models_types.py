from enum import Enum


class GenderEnum(Enum):
    MALE = "мужчина"
    FEMALE = "женщина"


class PermissonEnum(Enum):
    CRUD_ROLE = "CRUD_ROLE"
    ASSIGN_ROLE = "ASSIGN_ROLE"
    FREE_FILMS = "FREE_FILMS"
    PAID_FILMS = "PAID_FILMS"
