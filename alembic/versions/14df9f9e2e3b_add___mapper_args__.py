"""add __mapper_args__

Revision ID: 14df9f9e2e3b
Revises: 8b4638468e7f
Create Date: 2025-02-04 12:36:23.938105

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '14df9f9e2e3b'
down_revision: Union[str, None] = '8b4638468e7f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
