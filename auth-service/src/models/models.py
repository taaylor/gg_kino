import uuid

from db.postgres import Base
from sqlalchemy import ForeignKey, String
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
