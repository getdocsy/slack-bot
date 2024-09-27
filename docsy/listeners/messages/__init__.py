import logging
from pathlib import Path
from slack_bolt import App
from docsy.github_manager import get_github_manager_for_team
import docsy.shared
logger = logging.getLogger(__name__)

ai = docsy.shared.ai
db = docsy.shared.db

def is_valid_path(string):
    try:
        Path(string)  # Attempt to create a Path object
        return True
    except ValueError:
        return False

def message_im_callback(message, client, say):
    # breakpoint()
    # message_ts = message["ts"]
    history = client.conversations_history(
      channel=message["channel"],
      limit=10 # Precautionary measure: do not fetch 100 messages (which is the default)
    )

    messages = [
        (m["user"], m["text"])
        for m in history["messages"]
        if "user" in m and "text" in m
    ]

    team_id = message["team"]
    gitHubManager = get_github_manager_for_team(db, team_id)
    file_paths = gitHubManager.list_md_files()


    next_action = ai.get_next_action(messages, file_paths)
    match next_action:
        case "SYSTEM_CREATE_PR":
            text = "Should I create a PR against our public docs with what we have discussed?"
            say(
            blocks=[
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": text,
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
            text=text,
            )
        case _: 
            say(
                text=next_action,
            )

def register(app: App):
    app.message("")(message_im_callback)
