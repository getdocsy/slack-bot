from slack_bolt import App
from .app_home_opened import app_home_opened_callback
from .app_mention import app_mention_callback

# bolt is spamming the logs with warnings if we don't handle this events
def handle_message_events():
    return

def register(app: App):
    app.event("app_mention")(app_mention_callback)
    app.event("app_home_opened")(app_home_opened_callback)
    app.event("message")(handle_message_events)
