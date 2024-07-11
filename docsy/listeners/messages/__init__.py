import re

from slack_bolt import App
from .sample_message import sample_message_callback


def message_learned_callback(message, say):
    thread_ts = message.get("thread_ts", None) or message["ts"]
    say(
        blocks=[
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"Hey there <@{message['user']}>! Looks like you learned something there. Should I create a PR against our public docs?",
                },
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "Yes, please"},
                        "action_id": "button_click_yes",
                    },
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "No, thanks"},
                        "action_id": "button_click_no",
                    },
                ],
            },
        ],
        text=f"Hey there <@{message['user']}>! Looks like you learned something there. Should I create a PR against our public docs?",
        thread_ts=thread_ts,
    )


def register(app: App):
    app.message(re.compile("(hi|hello|hey)"))(sample_message_callback)
    app.message("thanks")(message_learned_callback)
