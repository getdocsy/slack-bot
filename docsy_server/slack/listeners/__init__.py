from docsy_server.slack.listeners import actions
from docsy_server.slack.listeners import events
from docsy_server.slack.listeners import messages
from docsy_server.slack.listeners import views


def register_listeners(app):
    actions.register(app)
    events.register(app)
    messages.register(app)
    views.register(app)
