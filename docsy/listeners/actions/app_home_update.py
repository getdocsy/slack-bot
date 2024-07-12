from logging import Logger
import docsy.shared
from docsy.github_manager import get_github_manager

db = docsy.shared.db


def app_home_update_button_click_callback(ack, body, client, context, logger: Logger):
    ack()  # Acknowledge the button click

    new_docs_repo = body["view"]["state"]["values"]["docs_repo_input"][
        "docs_repo_input"
    ]["value"]
    new_content_subdir = body["view"]["state"]["values"]["content_subdir_input"][
        "content_subdir_input"
    ]["value"]
    team_id = body["team"]["id"]
    db.update_customer_docs_repo(
        team_id, new_docs_repo
    )  # TODO reload required to show new values
    db.update_customer_content_subdir(team_id, new_content_subdir)

    gitHubManager = get_github_manager(db, team_id)

    client.views_update(
        view_id=body["view"]["id"],
        view={
            "type": "home",
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*Hey <@"
                        + body["user"]["id"]
                        + ">, I'm Docsy. Nice to meet you! :wave:*",
                    },
                },
                {"type": "divider"},
                {
                    "type": "header",
                    "text": {"type": "plain_text", "text": "Configuration"},
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "Configure how Docsy behaves.",
                    },
                },
                {
                    "type": "input",
                    "block_id": "docs_repo_input",
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "docs_repo_input",
                        "initial_value": new_docs_repo,
                    },
                    "label": {
                        "type": "plain_text",
                        "text": "docs repo",
                        "emoji": False,
                    },
                },
                {
                    "type": "input",
                    "block_id": "content_subdir_input",
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "content_subdir_input",
                        "initial_value": new_content_subdir,
                    },
                    "label": {
                        "type": "plain_text",
                        "text": "content subdir",
                        "emoji": False,
                    },
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "Update",
                                "emoji": True,
                            },
                            "action_id": "app_home_update_button_click",
                        }
                    ],
                },
            ],
        },
    )
