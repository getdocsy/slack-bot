import logging
import docsy.shared
from docsy.github_manager import get_github_manager

logger = logging.getLogger(__name__)
db = docsy.shared.db


def app_home_update_button_click_callback(ack, body, client, context, logger):
    ack()  # Acknowledge the button click

    def get_new_value(key):
        result = body["view"]["state"]["values"][key][key]["value"]
        if result == "":
            return None
        return result

    new_organization_name = get_new_value("organization_name_input")
    new_github_app_installation_id = get_new_value("github_app_installation_id_input")
    new_docs_repo = get_new_value("docs_repo_input")
    new_content_subdir = get_new_value("content_subdir_input")
    new_sidebar_file_path = get_new_value("sidebar_file_path_input")
    team_id = body["team"]["id"]

    db.update_customer_organization_name(team_id, new_organization_name)
    db.update_customer_github_app_installation_id(
        team_id, new_github_app_installation_id
    )
    db.update_customer_docs_repo(team_id, new_docs_repo)
    db.update_customer_content_subdir(team_id, new_content_subdir)
    db.update_customer_sidebar_file_path(team_id, new_sidebar_file_path)

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
                        "text": "For more information on these options, see the <https://docs.getdocsy.com/|docs>.",
                    },
                },
                {
                    "type": "input",
                    "block_id": "organization_name_input",
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "organization_name_input",
                        "initial_value": new_organization_name or "",
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
                        "initial_value": str(new_github_app_installation_id or ""),
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
                        "initial_value": new_docs_repo or "",
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
                        "initial_value": new_content_subdir or "",
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
                        "initial_value": new_sidebar_file_path or "",
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
