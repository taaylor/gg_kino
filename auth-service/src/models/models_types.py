from enum import Enum


class GenderEnum(str, Enum):
    MALE = "мужчина"
    FEMALE = "женщина"


class RoleEnum(str, Enum):
    ADMIN = "ADMIN"
    SUB_USER = "SUB_USER"
    UNSUB_USER = "UNSUB_USER"
    ANONYMOUS = "ANONYMOUS"


class PermissionEnum(str, Enum):
    CRUD_ROLE = "CRUD_ROLE"
    ASSIGN_ROLE = "ASSIGN_ROLE"
    FREE_FILMS = "FREE_FILMS"
    PAID_FILMS = "PAID_FILMS"
