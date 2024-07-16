import logging
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base

from alembic import command
from alembic.config import Config
import os

logger = logging.getLogger(__name__)
Base = declarative_base()


class Customer(Base):
    __tablename__ = "customers"
    team_id = Column(String, primary_key=True)
    organization_name = Column(String, nullable=True)
    github_app_installation_id = Column(Integer, nullable=True)
    docs_repo = Column(String, nullable=True)
    content_subdir = Column(String, nullable=True)


def get_engine(db_path):
    return create_engine(f"sqlite:///{db_path}")


def initialize_database(engine):
    Base.metadata.create_all(engine)


def _run_alembic_upgrade():
    # Assuming your alembic.ini file is in the same directory as this script
    alembic_cfg = Config(os.path.join(os.path.dirname(__file__), "alembic.ini"))
    # Run the upgrade to the 'head' revision
    command.upgrade(alembic_cfg, "head")


Session = sessionmaker()


class Database:
    def __init__(self, db_path):
        self.engine = get_engine(db_path)
        initialize_database(self.engine)
        _run_alembic_upgrade()
        Session.configure(bind=self.engine)
        self.session = Session()

    def get_customer(self, team_id):
        customer = self.session.query(Customer).filter_by(team_id=team_id).first()
        if customer:
            return customer
        else:
            raise ValueError(f"No customer found for team_id: {team_id}")

    def customer_exists(self, team_id):
        customer = self.session.query(Customer).filter_by(team_id=team_id).first()
        if customer:
            return True
        else:
            return False

    def insert_customer(self, customer_data):
        customer = Customer(**customer_data)
        self.session.add(customer)
        self.session.commit()

    def update_customer_organization_name(self, team_id, new_organization_name):
        customer = self.get_customer(team_id)
        customer.organization_name = new_organization_name
        self.session.commit()

    def update_customer_github_app_installation_id(
        self, team_id, new_github_app_installation_id
    ):
        customer = self.get_customer(team_id)
        customer.github_app_installation_id = new_github_app_installation_id
        self.session.commit()

    def update_customer_docs_repo(self, team_id, new_docs_repo):
        customer = self.get_customer(team_id)
        customer.docs_repo = new_docs_repo
        self.session.commit()

    def update_customer_content_subdir(self, team_id, new_content_subdir):
        customer = self.get_customer(team_id)
        customer.content_subdir = new_content_subdir
        self.session.commit()
