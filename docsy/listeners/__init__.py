from docsy.listeners import actions
from docsy.listeners import commands
from docsy.listeners import events
from docsy.listeners import messages
from docsy.listeners import shortcuts
from docsy.listeners import views


def register_listeners(app):
    actions.register(app)
    commands.register(app)
    events.register(app)
    messages.register(app)
    shortcuts.register(app)
    views.register(app)
