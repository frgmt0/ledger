"""description of change

Revision ID: 555b95d528b0
Revises: initial_schema
Create Date: 2025-01-20 19:20:54.844621

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '555b95d528b0'
down_revision: Union[str, None] = 'initial_schema'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
