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
                "sidebar_file_path": None,
                "front_matter": None,
                "blacklist": None,
                "base_branch": None,
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
                        "type": "input",
                        "block_id": "sidebar_file_path_input",
                        "element": {
                            "type": "plain_text_input",
                            "action_id": "sidebar_file_path_input",
                            "initial_value": db.get_customer(
                                context.team_id
                            ).sidebar_file_path
                            or "",
                        },
                        "label": {
                            "type": "plain_text",
                            "text": "sidebar file path",
                            "emoji": False,
                        },
                        "hint": {
                            "type": "plain_text",
                            "text": "The path to the sidebar file in the repository. This file is updated when new files are added to the documentation. If not set, the sidebar will not be updated.",
                        },
                    },
                    {
                        "type": "input",
                        "block_id": "front_matter_input",
                        "element": {
                            "type": "plain_text_input",
                            "multiline": True,
                            "action_id": "front_matter_input",
                            "initial_value": db.get_customer(
                                context.team_id
                            ).front_matter
                            or "",
                        },
                        "label": {
                            "type": "plain_text",
                            "text": "Front matter example",
                            "emoji": True,
                        },
                        "hint": {
                            "type": "plain_text",
                            "text": "Enter an example of the front matter you use in your markdown files. Docsy will use this to create new files.",
                        },
                    },
                    {
                        "type": "input",
                        "block_id": "blacklist_input",
                        "element": {
                            "type": "plain_text_input",
                            "multiline": True,
                            "action_id": "blacklist_input",
                            "initial_value": db.get_customer(context.team_id).blacklist
                            or "",
                        },
                        "label": {
                            "type": "plain_text",
                            "text": "Black list",
                            "emoji": True,
                        },
                        "hint": {
                            "type": "plain_text",
                            "text": "Enter words you want to blacklist, separated by commas. Docsy will not open pull requests with any of those words.",
                        },
                    },
                    {
                        "type": "input",
                        "block_id": "base_branch_input",
                        "element": {
                            "type": "plain_text_input",
                            "action_id": "base_branch_input",
                            "initial_value": db.get_customer(context.team_id).base_branch
                            or "",
                        },
                        "label": {
                            "type": "plain_text",
                            "text": "base branch file path",
                            "emoji": False,
                        },
                        "hint": {
                            "type": "plain_text",
                            "text": "The name of the branch you want the changes pulled into. This must be an existing branch on the current repository.",
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
