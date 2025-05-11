"""init session tabs

Revision ID: 715c40ff5e28
Revises: 1b93bf7fe8b2
Create Date: 2025-04-22 23:16:03.996359

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "715c40ff5e28"
down_revision: Union[str, None] = "1b93bf7fe8b2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Создание основной таблицы
    op.execute("CREATE SCHEMA IF NOT EXISTS session")

    op.create_table(
        "user_sessions",
        sa.Column(
            "session_id",
            sa.UUID(),
            nullable=False,
            comment="Уникальный идентификатор сессии",
        ),
        sa.Column(
            "user_id",
            sa.UUID(),
            nullable=False,
            comment="Уникальный идентификатор пользователя",
        ),
        sa.Column(
            "user_agent",
            sa.String(length=255),
            nullable=True,
            comment="Клиентское устройство пользователя",
        ),
        sa.Column(
            "refresh_token",
            sa.String(),
            nullable=False,
            comment="Рефреш токен пользовательской сессии (JWT)",
        ),
        sa.Column("expires_at", sa.DateTime(), nullable=False, comment="Дата истечения сессии"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("session_id"),
        schema="session",
    )

    op.create_table(
        "user_sessions_hist",
        sa.Column(
            "session_id",
            sa.UUID(),
            nullable=False,
            comment="Уникальный идентификатор сессии",
        ),
        sa.Column(
            "user_id",
            sa.UUID(),
            nullable=False,
            comment="Уникальный идентификатор пользователя",
        ),
        sa.Column(
            "user_agent",
            sa.String(length=255),
            nullable=True,
            comment="Клиентское устройство пользователя",
        ),
        sa.Column("expires_at", sa.DateTime(), nullable=False, comment="Дата истечения сессии"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("user_id", "session_id"),
        postgresql_partition_by="HASH (user_id)",
        schema="session",
    )

    # Создание партиций
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS session.user_sessions_hist_p0 PARTITION OF session.user_sessions_hist
        FOR VALUES WITH (MODULUS 4, REMAINDER 0);
        """
    )
    op.execute(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS idx_user_sessions_hist_p0_user_id
        ON session.user_sessions_hist_p0 (user_id, session_id);
        """
    )

    op.execute(
        """
        CREATE TABLE IF NOT EXISTS session.user_sessions_hist_p1 PARTITION OF session.user_sessions_hist
        FOR VALUES WITH (MODULUS 4, REMAINDER 1);
        """
    )
    op.execute(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS idx_user_sessions_hist_p1_user_id
        ON session.user_sessions_hist_p1 (user_id, session_id);
        """
    )

    op.execute(
        """
        CREATE TABLE IF NOT EXISTS session.user_sessions_hist_p2 PARTITION OF session.user_sessions_hist
        FOR VALUES WITH (MODULUS 4, REMAINDER 2);
        """
    )
    op.execute(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS idx_user_sessions_hist_p2_user_id
        ON session.user_sessions_hist_p2 (user_id, session_id);
        """
    )

    op.execute(
        """
        CREATE TABLE IF NOT EXISTS session.user_sessions_hist_p3 PARTITION OF session.user_sessions_hist
        FOR VALUES WITH (MODULUS 4, REMAINDER 3);
        """
    )
    op.execute(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS idx_user_sessions_hist_p3_user_id
        ON session.user_sessions_hist_p3 (user_id, session_id);
        """
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Удаление партиций
    op.execute("DROP TABLE IF EXISTS session.user_sessions_hist_p0")
    op.execute("DROP TABLE IF EXISTS session.user_sessions_hist_p1")
    op.execute("DROP TABLE IF EXISTS session.user_sessions_hist_p2")
    op.execute("DROP TABLE IF EXISTS session.user_sessions_hist_p3")

    # Удаление основных таблиц
    op.drop_table("user_sessions_hist", schema="session")
    op.drop_table("user_sessions", schema="session")
