"""create schema

Revision ID: 2a04401f9855
Revises:
Create Date: 2025-07-26 14:06:34.047884+00:00

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "2a04401f9855"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("CREATE SCHEMA IF NOT EXISTS recs_profile")


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP SCHEMA IF EXISTS recs_profile")
