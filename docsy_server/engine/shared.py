from docsy_server.engine.ai import AI
from docsy_server.engine.github_manager import GitHubManager
from docsy_server.engine.database import Database

ai = AI()
db = Database("./data/db.sqlite")
