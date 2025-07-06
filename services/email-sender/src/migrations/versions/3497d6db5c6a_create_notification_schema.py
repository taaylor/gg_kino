"""create notification schema

Revision ID: 3497d6db5c6a
Revises:
Create Date: 2025-07-06 12:13:01.143950

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "3497d6db5c6a"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.execute("CREATE SCHEMA IF NOT EXISTS notification")


def downgrade():
    op.execute("DROP SCHEMA IF EXISTS notification")
