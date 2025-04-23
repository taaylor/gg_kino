import uuid

from db.postgres import Base
from models.models_types import GenderEnum
from sqlalchemy import ForeignKey, PrimaryKeyConstraint, String
from sqlalchemy.orm import Mapped, mapped_column, relationship


class User(Base):
    __tablename__ = "user"
    __table_args__ = {"schema": "profile"}

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    username: Mapped[str] = mapped_column(String(50), unique=True)
    first_name: Mapped[str | None] = mapped_column(String(50))
    last_name: Mapped[str | None] = mapped_column(String(50))
    gender: Mapped[GenderEnum | None]
    role_code: Mapped[str] = mapped_column(ForeignKey("profile.dict_roles.role"))

    # обратная orm связь с ролью (many-to-one)
    role: Mapped["DictRoles"] = relationship(
        "DictRoles",
        back_populates="users",
    )

    # обратная orm связь с cred (one-to-one)
    user_cred: Mapped["UserCred"] = relationship(
        "UserCred",
        back_populates="user",
        uselist=False,
        lazy="joined",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<{self.__class__.__name__}(id={self.id}, username={self.username})>"

    def __str__(self):
        return f"Модель: {self.__class__.__name__}(id={self.id}, username={self.username})"


class UserCred(Base):
    __tablename__ = "user_cred"
    __table_args__ = {"schema": "profile"}

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("profile.user.id"), primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    password: Mapped[str] = mapped_column(String(255))

    # обратная orm связь с user (one-to-one)
    user: Mapped["User"] = relationship("User", back_populates="user_cred", uselist=False)

    def __repr__(self):
        return f"<{self.__class__.__name__}(user_id={self.user_id})>"

    def __str__(self):
        return f"Модель: {self.__class__.__name__}(user_id={self.user_id})"


class DictRoles(Base):
    __tablename__ = "dict_roles"
    __table_args__ = {"schema": "profile"}

    role: Mapped[str] = mapped_column(String(50), primary_key=True)
    descriptions: Mapped[str | None] = mapped_column(String(500))

    # обратная связь с user (one-to-many)
    users: Mapped[list["User"]] = relationship("User", back_populates="role")

    # обратная связь с permission (one-to-many)
    permissions: Mapped[list["RolesPermissions"]] = relationship(
        "RolesPermissions", back_populates="role", lazy="joined"
    )

    def __repr__(self):
        return f"<{self.__class__.__name__}(role={self.role})>"

    def __str__(self):
        return f"Модель: {self.__class__.__name__}(role={self.role})"


class RolesPermissions(Base):
    __tablename__ = "roles_permissions"
    __table_args__ = (
        PrimaryKeyConstraint("role_code", "permission", name="role_permission_pk"),
        {"schema": "profile"},
    )

    role_code: Mapped[str] = mapped_column(ForeignKey("profile.dict_roles.role"))
    permission: Mapped[str] = mapped_column(String(50))
    descriptions: Mapped[str | None] = mapped_column(String(500))

    # обратная связь с role
    role: Mapped["DictRoles"] = relationship("DictRoles", back_populates="permission")

    def __repr__(self):
        return f"<{self.__class__.__name__}(permission={self.permission})>"

    def __str__(self):
        return f"Модель: {self.__class__.__name__}(permission={self.permission})"
