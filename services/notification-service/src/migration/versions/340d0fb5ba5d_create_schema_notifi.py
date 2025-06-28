"""create schema notifi

Revision ID: 340d0fb5ba5d
Revises:
Create Date: 2025-06-27 19:11:06.585662

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "340d0fb5ba5d"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("CREATE SCHEMA IF NOT EXISTS notification")
    op.execute("CREATE SCHEMA IF NOT EXISTS global_notification")


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP SCHEMA IF EXISTS notification")
    op.execute("DROP SCHEMA IF EXISTS global_notification")
