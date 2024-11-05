from logging import Logger
from docsy.engine import db


def create_input_block(label, block_id, hint, team_id, multiline=False):

    def get_attr_name(block_id):
        return block_id.replace("_input", "")

    return {
        "type": "input",
        "block_id": block_id,
        "element": {
            "type": "plain_text_input",
            "multiline": multiline,
            "action_id": block_id,
            "initial_value": str(
                getattr(db.get_customer(team_id), get_attr_name(block_id)) or ""
            ),
        },
        "label": {
            "type": "plain_text",
            "text": label,
            "emoji": False,
        },
        "hint": {
            "type": "plain_text",
            "text": hint,
        },
    }


def get_config_blocks(team_id, user_id):
    return [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Hey <@{user_id}>, I'm Docsy. Nice to meet you! :wave:*",
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
        create_input_block(
            label="Organization Name",
            block_id="organization_name_input",
            hint="How should Docsy refer to your organization?",
            team_id=team_id,
        ),
        create_input_block(
            label="GitHub App Installation ID",
            block_id="github_app_installation_id_input",
            hint="This is the ID of the GitHub app installation. You can find it in the GitHub app settings.",
            team_id=team_id,
        ),
        create_input_block(
            label="Docs Repo",
            block_id="docs_repo_input",
            hint="The name of the repository where the documentation is stored. Format is owner/repo.",
            team_id=team_id,
        ),
        create_input_block(
            label="Base Branch",
            block_id="base_branch_input",
            hint="The name of the branch against which Docsy should open pull requests. Default is main.",
            team_id=team_id,
        ),
        create_input_block(
            label="Content Subdirectory",
            block_id="content_subdir_input",
            hint="The subdirectory in the repository where markdown files are stored. Default is root.",
            team_id=team_id,
        ),
        create_input_block(
            label="Sidebar File Path",
            block_id="sidebar_file_path_input",
            hint="The path to the sidebar file in the repository. This file is updated when new files are added to the documentation. If not set, the sidebar will not be updated.",
            team_id=team_id,
        ),
        create_input_block(
            label="Front Matter",
            block_id="front_matter_input",
            hint="Enter an example of the front matter you use in your markdown files. Docsy will use this to create new files.",
            multiline=True,
            team_id=team_id,
        ),
        create_input_block(
            label="Blacklist",
            block_id="blacklist_input",
            hint="Enter words you want to blacklist, separated by commas. Docsy will not open pull requests with any of those words.",
            multiline=True,
            team_id=team_id,
        ),
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
    ]
