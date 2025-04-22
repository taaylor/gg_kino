import uuid
from datetime import datetime

from db.postgres import Base
from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship


class User(Base):
    __tablename__ = "user"
    __table_args__ = {"schema": "profile"}

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    first_name: Mapped[str] = mapped_column(String(50), nullable=True)
    last_name: Mapped[str | None] = mapped_column(String(50), nullable=True)
    gender: Mapped[str | None] = mapped_column(String(50), nullable=True)

    user_cred: Mapped["UserCred"] = relationship(
        "UserCred",
        back_populates="user",
        uselist=False,
        lazy="joined",
        cascade="all, delete-orphan",
    )

    def __str__(self):
        return f"<User(id={self.id}, username={self.username})>"


class UserCred(Base):
    __tablename__ = "user_cred"
    __table_args__ = {"schema": "profile"}

    user_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("profile.user.id"), primary_key=True
    )
    email: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="user_cred", uselist=False)


class UserSession(Base):
    __tablename__ = "user_sessions"
    __table_args__ = {"schema": "session"}

    session_id: Mapped[UUID] = mapped_column(
        UUID, primary_key=True, default=uuid.uuid4, comment="Уникальный идентификатор сессии"
    )
    user_id: Mapped[UUID] = mapped_column(
        UUID, nullable=False, comment="Уникальный идентификатор пользователя"
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


class UserSessionsHist(Base):
    __tablename__ = "user_sessions_hist"
    __table_args__ = {"schema": "session"}

    session_id: Mapped[UUID] = mapped_column(
        UUID, primary_key=True, comment="Уникальный идентификатор сессии"
    )
    user_id: Mapped[UUID] = mapped_column(
        UUID, nullable=False, comment="Уникальный идентификатор пользователя"
    )
    user_agent: Mapped[str | None] = mapped_column(
        String(255), comment="Клиентское устройство пользователя"
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, comment="Дата истечения сессии"
    )
