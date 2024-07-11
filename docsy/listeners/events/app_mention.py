def app_mention_callback(message, say):
    thread_ts = message.get("thread_ts", None) or message["ts"]
    say(
        blocks=[
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"Hey there <@{message['user']}>, thanks for summoning me! Should I create a PR against our public docs?",
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
        text=f"Hey there <@{message['user']}>, thanks for summoning me! Should I create a PR against our public docs?",
        thread_ts=thread_ts,
    )
