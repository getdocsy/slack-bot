"""insert customers

Revision ID: efbf4104118e
Revises:
Create Date: 2024-07-15 14:40:44.154933

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


from sqlalchemy.orm import sessionmaker

from docsy.database import Customer, get_engine

# revision identifiers, used by Alembic.
revision: str = "efbf4104118e"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Bind the engine to the metadata of the Base class so that the
    # declaratives can be accessed through a DBSession instance
    engine = get_engine("./data/db")
    Session = sessionmaker(bind=engine)
    session = Session()

    # Insert data
    session.add_all(
        [
            Customer(
                team_id="T0692AWNLLC",
                organization_name="Laufvogel Company",
                github_app_installation_id=51286673,
                docs_repo="felixzieger/congenial-computing-machine",
                content_subdir="meshcloud-docs/docs/",
            ),
            Customer(
                team_id="T07786H8B42",
                organization_name="Docsy Company",
                github_app_installation_id=51663706,
                docs_repo="getdocsy/docs",
                content_subdir="docs/",
            ),
        ]
    )
    session.commit()


def downgrade():
    # Bind the engine to the metadata of the Base class so that the
    # declaratives can be accessed through a DBSession instance
    engine = get_engine("./data/db")
    Session = sessionmaker(bind=engine)
    session = Session()

    # Remove the inserted data
    session.query(Customer).filter(
        Customer.team_id.in_(["T0692AWNLLC", "T07786H8B42"])
    ).delete(synchronize_session=False)
    session.commit()
