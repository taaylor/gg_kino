import uuid
import logging
from datetime import datetime

from db.postgres import Base
from models.models_types import GenderEnum
from sqlalchemy import DateTime, ForeignKey, PrimaryKeyConstraint, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

logger = logging.getLogger(__name__)


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
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<{self.__class__.__name__}(id={self.id}, username={self.username})>"

    def __str__(self):
        return f"Модель: {self.__class__.__name__}(id={self.id}, username={self.username})"


class UserCred(Base):
    __tablename__ = "user_cred"
    __table_args__ = {"schema": "profile"}

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("profile.user.id", ondelete="CASCADE"), primary_key=True
    )
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
        "RolesPermissions",
        back_populates="role",
        cascade="all, delete-orphan",
        passive_deletes=True,  # БД сама удаляет связанные данные
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

    role_code: Mapped[str] = mapped_column(
        ForeignKey("profile.dict_roles.role", ondelete="CASCADE")
    )
    permission: Mapped[str] = mapped_column(String(50))
    descriptions: Mapped[str | None] = mapped_column(String(500))

    # обратная связь с role
    role: Mapped["DictRoles"] = relationship("DictRoles", back_populates="permissions")

    def __repr__(self):
        return f"<{self.__class__.__name__}(permission={self.permission})>"

    def __str__(self):
        return f"Модель: {self.__class__.__name__}(permission={self.permission})>"


class UserSession(Base):
    __tablename__ = "user_sessions"
    __table_args__ = {"schema": "session"}

    session_id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4, comment="Уникальный идентификатор сессии"
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        nullable=False, comment="Уникальный идентификатор пользователя"
    )
    user_agent: Mapped[str | None] = mapped_column(
        String(255), comment="Клиентское устройство пользователя"
    )
    refresh_token: Mapped[str] = mapped_column(
        String, nullable=False, comment="Рефреш токен пользовательской сессии (JWT)"
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, comment="Дата истечения сессии"
    )


def create_partition(target, connection, **kwargs) -> None:
    """Создание партиций для user_sessions_hist."""
    logger.info("Создание партиций для таблицы user_sessions_hist")
    connection.execute(
        text(
            """CREATE TABLE IF NOT EXISTS "users_sign_in_smart" PARTITION OF "user_session_hist" FOR VALUES IN ('TV')"""
        )
    )
    connection.execute(
        text(
            """CREATE TABLE IF NOT EXISTS "users_sign_in_mobile" PARTITION OF "user_session_hist" FOR VALUES IN ('PHONE')"""
        )
    )
    connection.execute(
        text(
            """CREATE TABLE IF NOT EXISTS "users_sign_in_web" PARTITION OF "user_session_hist" FOR VALUES IN ('WEB')"""
        )
    )
    logger.info("Партиции успешно созданы")


class UserSessionsHist(Base):
    __tablename__ = "user_sessions_hist"
    __table_args__ = (
        {
            "schema": "session",
            "postgresql_partition_by": "LIST (user_device_type)",
            "listeners": [("after_create", create_partition)],
        },
    )

    session_id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, comment="Уникальный идентификатор сессии"
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        nullable=False, comment="Уникальный идентификатор пользователя"
    )
    user_agent: Mapped[str | None] = mapped_column(
        String(255), comment="Клиентское устройство пользователя"
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, comment="Дата истечения сессии"
    )
    user_device_type: Mapped[str] = mapped_column(
        default="WEB", primary_key=True, comment="Тип устройства пользователя"
    )
