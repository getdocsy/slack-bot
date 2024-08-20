import logging
import json
import docsy.shared
from docsy.github_manager import get_github_manager
from docsy.listeners.views.app_home import get_config_blocks

logger = logging.getLogger(__name__)
db = docsy.shared.db


def app_home_update_button_click_callback(ack, body, client, context, logger):
    ack()  # Acknowledge the button click

    def get_new_value(key):
        result = body["view"]["state"]["values"][key][key]["value"]
        if result == "":
            return None
        return result

    team_id = body["team"]["id"]

    current_customer_data = db.get_customer(team_id).__dict__
    current_customer_data.pop("_sa_instance_state")  # Remove SQLAlchemy state attribute

    new_customer_data = {
        "organization_name": get_new_value("organization_name_input"),
        "github_app_installation_id": get_new_value("github_app_installation_id_input"),
        "docs_repo": get_new_value("docs_repo_input"),
        "content_subdir": get_new_value("content_subdir_input"),
        "sidebar_file_path": get_new_value("sidebar_file_path_input"),
        "front_matter": get_new_value("front_matter_input"),
        "blacklist": get_new_value("blacklist_input"),
        "base_branch": get_new_value("base_branch_input"),
    }

    if current_customer_data == new_customer_data:
        return

    username = body["user"]["username"]
    db.insert_event(
        {
            "title": "User updates configuration in app home",
            "description": f"User {username} updates configuration in app home",
            "author": username,
            "previous_content": json.dumps(current_customer_data),
            "content": json.dumps(new_customer_data),
            "team_id": team_id,
        }
    )
    db.update_customer(team_id, new_customer_data)

    client.views_update(
        view_id=body["view"]["id"],
        view={
            "type": "home",
            "blocks": get_config_blocks(team_id=team_id, user_id=body["user"]["id"]),
        },
    )
