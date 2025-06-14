from loguru import logger
from slack_bolt import App
from docsy.engine.github_manager import (
    get_github_manager_for_team,
    GitHubManagerException,
)
from docsy.engine import slack_ai as ai, db
from docsy.slack.listeners.views.app_home import is_configuration_complete


def message_im_callback(message, client, say):
    try:
        ts = message["thread_ts"]
    except KeyError:
        ts = message["ts"]

    history = client.conversations_replies(
        channel=message["channel"],
        ts=ts,
    )

    messages = [
        (m["user"], m["text"])
        for m in history["messages"]
        if "user" in m and "text" in m
    ]

    team_id = message["team"]
    
    if not is_configuration_complete(team_id):
        say(
            text="I need to be configured before I can help you. Please visit my app home to complete the setup.",
            thread_ts=ts,
        )
        return

    try:
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
                                    "text": {
                                        "type": "plain_text",
                                        "text": "Yes, please",
                                    },
                                    "action_id": "button_click_yes",
                                },
                                {
                                    "type": "button",
                                    "text": {
                                        "type": "plain_text",
                                        "text": "No, thanks",
                                    },
                                    "action_id": "button_click_no",
                                },
                            ],
                        },
                    ],
                    text=text,
                    thread_ts=ts,
                )
            case "SYSTEM_DISCUSS":
                text = ai.discuss(messages, file_paths)
                say(text=text, thread_ts=ts)
            case _:
                say(text=next_action, thread_ts=ts)
    except GitHubManagerException:
        say(
            text="I failed to connect to your GitHub organization. Please check the configuration in app home.",
            thread_ts=ts,
        )


def register(app: App):
    app.message("")(message_im_callback)
