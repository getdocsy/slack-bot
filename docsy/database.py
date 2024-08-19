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
    sidebar_file_path = Column(String, nullable=True)
    front_matter = Column(String, nullable=True)
    blacklist = Column(String, nullable=True)
    base_branch = Column(String, nullable=True)


def get_engine(db_path):
    return create_engine(f"sqlite:///{db_path}")


def initialize_database(engine):
    Base.metadata.create_all(engine)
    alembic_cfg = Config(os.path.join(os.path.dirname(__file__), "alembic.ini"))
    # Do not run migrations for new databases
    command.stamp(alembic_cfg, "head")


def run_alembic_upgrade():
    alembic_cfg = Config(os.path.join(os.path.dirname(__file__), "alembic.ini"))
    command.upgrade(alembic_cfg, "head")


Session = sessionmaker()


class Database:
    def __init__(self, db_path):
        self.engine = get_engine(db_path)

        # Only initialize the database if it doesn't exist
        if not os.path.exists(os.path.dirname(db_path)):
            os.makedirs(os.path.dirname(db_path))
            initialize_database(self.engine)
        else:
            run_alembic_upgrade()

        Session.configure(bind=self.engine)
        self.session = Session()

    def get_customer(self, team_id):
        customer = self.session.query(Customer).filter_by(team_id=team_id).first()
        if customer:
            return customer
        else:
            raise ValueError(f"No customer found for team_id: {team_id}")

    def get_customer_blacklist(self, team_id):
        customer = self.get_customer(team_id)
        return (
            [
                word.strip() for word in customer.blacklist.split(",")
            ]  # Remove whitespace and split by comma
            if customer.blacklist
            else []
        )

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

    def update_customer(self, team_id, customer_data):
        customer = self.get_customer(team_id)
        for key, value in customer_data.items():
            setattr(customer, key, value)
        self.session.commit()
