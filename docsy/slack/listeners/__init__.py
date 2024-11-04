from docsy.slack.listeners import actions
from docsy.slack.listeners import events
from docsy.slack.listeners import messages
from docsy.slack.listeners import views


def register_listeners(app):
    actions.register(app)
    events.register(app)
    messages.register(app)
    views.register(app)
