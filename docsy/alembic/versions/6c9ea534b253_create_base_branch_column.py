"""create base_branch column

Revision ID: 6c9ea534b253
Revises: ea0102c1f7f0
Create Date: 2024-08-19 12:20:38.618897

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6c9ea534b253'
down_revision: Union[str, None] = 'ea0102c1f7f0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column("customers", sa.Column("base_branch", sa.Text(), nullable=True))


def downgrade():
    op.drop_column("customers", "base_branch")
