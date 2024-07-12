from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base

Base = declarative_base()


class Customer(Base):
    __tablename__ = "customers"
    team_id = Column(String, primary_key=True)
    organization_name = Column(String, nullable=False)
    github_app_installation_id = Column(Integer, nullable=False)
    docs_repo = Column(String, nullable=False)
    content_subdir = Column(String, nullable=False)


def get_engine(db_path):
    return create_engine(f"sqlite:///{db_path}")


def initialize_database(engine):
    Base.metadata.create_all(engine)


Session = sessionmaker()


class Database:
    def __init__(self, db_path):
        self.engine = get_engine(db_path)
        initialize_database(self.engine)
        Session.configure(bind=self.engine)
        self.session = Session()

    def get_customer(self, team_id):
        customer = self.session.query(Customer).filter_by(team_id=team_id).first()
        if customer:
            return customer
        else:
            raise ValueError(f"No customer found for team_id: {team_id}")

    def insert_customer(self, customer_data):
        customer = Customer(**customer_data)
        self.session.add(customer)
        self.session.commit()

    def update_customer_docs_repo(self, team_id, new_docs_repo):
        customer = self.get_customer(team_id)
        customer.docs_repo = new_docs_repo
        self.session.commit()

    def update_customer_content_subdir(self, team_id, new_content_subdir):
        customer = self.get_customer(team_id)
        customer.content_subdir = new_content_subdir
        self.session.commit()


db = Database("./data/db")

# db.insert_customer(
#     {
#         "team_id": "T0692AWNLLC",
#         "organization_name": "Laufvogel Company",
#         "github_app_installation_id": 51286673,
#         "docs_repo": "felixzieger/congenial-computing-machine",
#         "content_subdir": "meshcloud-docs/docs/",
#     },
# )

# db.insert_customer(
#     {
#         "team_id": "T07786H8B42",
#         "organization_name": "Docsy Company",
#         "github_app_installation_id": 51663706,
#         "docs_repo": "getdocsy/docs",
#         "content_subdir": "docs/",
#     },
# )
