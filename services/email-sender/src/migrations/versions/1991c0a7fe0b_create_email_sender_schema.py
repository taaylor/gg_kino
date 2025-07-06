"""create email_sender schema

Revision ID: 1991c0a7fe0b
Revises:
Create Date: 2025-07-06 17:07:32.719885

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "1991c0a7fe0b"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.execute("CREATE SCHEMA IF NOT EXISTS email_sender")


def downgrade():
    op.execute("DROP SCHEMA IF EXISTS email_sender")
