from slack_bolt import App
from .app_home_opened import app_home_opened_callback
from .app_mention import app_mention_callback


def register(app: App):
    app.event("app_mention")(app_mention_callback)
    app.event("app_home_opened")(app_home_opened_callback)  # Example\n\n
