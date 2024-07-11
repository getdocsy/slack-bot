import re

from slack_bolt import App
from .sample_message import sample_message_callback
from .message_learned import message_learned_callback


# To receive messages from a channel or dm your app must be a member!
def register(app: App):
    app.message(re.compile("(hi|hello|hey)"))(sample_message_callback)
    app.message("thanks")(message_learned_callback)
