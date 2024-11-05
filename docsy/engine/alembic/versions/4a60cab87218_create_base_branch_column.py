"""create base_branch column

Revision ID: 4a60cab87218
Revises: ea0102c1f7f0
Create Date: 2024-08-19 19:34:25.305643

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "4a60cab87218"
down_revision: Union[str, None] = "ea0102c1f7f0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("customers", sa.Column("base_branch", sa.VARCHAR(150), nullable=True))


def downgrade() -> None:
    op.drop_column("customers", "base_branch")
