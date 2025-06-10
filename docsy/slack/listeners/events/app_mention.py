from docsy.slack.listeners.views.app_home import is_configuration_complete

def app_mention_callback(event, say):
    user = event["user"]
    team_id = event["team"]
    thread_ts = event.get("thread_ts", None) or event["ts"]

    if not is_configuration_complete(team_id):
        say(
            blocks=[
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"Hey there <@{user}>, I need to be configured before I can help you. Please visit my app home to complete the setup.",
                    },
                },
            ],
            text=f"Hey there <@{user}>, I need to be configured before I can help you. Please visit my app home to complete the setup.",
            thread_ts=thread_ts,
        )
        return

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
