"""Add new front matter and blacklist columns to table

Revision ID: ea0102c1f7f0
Revises: efbf4104118e
Create Date: 2024-07-30 21:25:18.208696

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "ea0102c1f7f0"
down_revision: Union[str, None] = "efbf4104118e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column("customers", sa.Column("front_matter", sa.Text(), nullable=True))
    op.add_column("customers", sa.Column("blacklist", sa.Text(), nullable=True))


def downgrade():
    op.drop_column("customers", "front_matter")
    op.drop_column("customers", "blacklist")
