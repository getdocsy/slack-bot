from logging import Logger
import docsy.shared

db = docsy.shared.db


def app_home_opened_callback(client, event, context, logger: Logger):
    # ignore the app_home_opened event for anything but the Home tab
    if event["tab"] != "home":
        return
    try:
        client.views_publish(
            user_id=event["user"],
            view={
                "type": "home",
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "*Hey <@"
                            + event["user"]
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
                            "initial_value": db.get_customer(context.team_id).docs_repo,
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
                            "initial_value": db.get_customer(
                                context.team_id
                            ).content_subdir,
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
    except Exception as e:
        logger.error(f"Error publishing home tab: {e}")
