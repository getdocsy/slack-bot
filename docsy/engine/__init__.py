from docsy.engine.ai import AI
from docsy.engine.slack_ai import AI as SlackAI
from docsy.engine.database import Database

ai = AI()
slack_ai = SlackAI()
db = Database("./data/db.sqlite")
