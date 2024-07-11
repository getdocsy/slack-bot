from slack_bolt import App
from .app_home_opened import app_home_opened_callback


def app_mention_callback(event, say):
    user = event["user"]
    thread_ts = event.get("thread_ts", None) or event["ts"]
    say(
        blocks=[
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"Hey there <@{user}>, thanks for summoning me! Should I create a PR against our public docs?",
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
        text=f"Hey there <@{user}>, thanks for summoning me! Should I create a PR against our public docs?",
        thread_ts=thread_ts,
    )


def register(app: App):
    app.event("app_mention")(app_mention_callback)
    app.event("app_home_opened")(app_home_opened_callback)  # Example\n
