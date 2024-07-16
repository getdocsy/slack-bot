from logging import Logger
import docsy.shared

db = docsy.shared.db


def app_home_opened_callback(client, event, context, logger: Logger):
    if not db.customer_exists(context.team_id):
        db.insert_customer(
            {
                "team_id": context.team_id,
                "organization_name": None,
                "github_app_installation_id": None,
                "docs_repo": None,
                "content_subdir": None,
            },
        )

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
                            "text": "For more information on these options, see the <https://docs.getdocsy.com/|docs>.",
                        },
                    },
                    {
                        "type": "input",
                        "block_id": "organization_name_input",
                        "element": {
                            "type": "plain_text_input",
                            "action_id": "organization_name_input",
                            "initial_value": db.get_customer(
                                context.team_id
                            ).organization_name
                            or "",
                        },
                        "label": {
                            "type": "plain_text",
                            "text": "organization name",
                            "emoji": False,
                        },
                        "hint": {
                            "type": "plain_text",
                            "text": "How should I refer to your organization?",
                        },
                    },
                    {
                        "type": "input",
                        "block_id": "github_app_installation_id_input",
                        "element": {
                            "type": "plain_text_input",
                            "action_id": "github_app_installation_id_input",
                            "initial_value": str(
                                db.get_customer(
                                    context.team_id
                                ).github_app_installation_id
                                or ""
                            ),
                        },
                        "label": {
                            "type": "plain_text",
                            "text": "GitHub app installation ID",
                            "emoji": False,
                        },
                        "hint": {
                            "type": "plain_text",
                            "text": "This is the ID of the GitHub app installation. You can find it in the GitHub app settings.",
                        },
                    },
                    {
                        "type": "input",
                        "block_id": "docs_repo_input",
                        "element": {
                            "type": "plain_text_input",
                            "action_id": "docs_repo_input",
                            "initial_value": db.get_customer(context.team_id).docs_repo
                            or "",
                        },
                        "label": {
                            "type": "plain_text",
                            "text": "docs repo",
                            "emoji": False,
                        },
                        "hint": {
                            "type": "plain_text",
                            "text": "The name of the repository where the documentation is stored. Format is owner/repo.",
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
                            ).content_subdir
                            or "",
                        },
                        "label": {
                            "type": "plain_text",
                            "text": "content subdir",
                            "emoji": False,
                        },
                        "hint": {
                            "type": "plain_text",
                            "text": "The subdirectory in the repository where markdown files are stored. Default is root.",
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
