from logging import Logger
from docsy.engine import db
from docsy.slack.listeners.views.app_home import get_config_blocks


def app_home_opened_callback(client, event, context, logger: Logger):
    if not db.customer_exists(context.team_id):
        db.insert_customer(
            {
                "team_id": context.team_id,
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
                "blocks": get_config_blocks(
                    team_id=context.team_id, user_id=event["user"]
                ),
            },
        )
    except Exception as e:
        logger.error(f"Error publishing home tab: {e}")
