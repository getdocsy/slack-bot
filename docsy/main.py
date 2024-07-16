import os
import logging

from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler
from slack_bolt.oauth.oauth_settings import OAuthSettings
from slack_sdk.oauth.installation_store import FileInstallationStore
from slack_sdk.oauth.state_store import FileOAuthStateStore

from docsy.listeners import register_listeners

from flask import Flask, request

logger = logging.getLogger(__name__)

# Docsy uses OAUTH for multi-workspace slack support
SLACK_SIGNING_SECRET = os.environ.get("SLACK_SIGNING_SECRET")
oauth_settings = OAuthSettings(
    client_id=os.environ["SLACK_CLIENT_ID"],
    client_secret=os.environ["SLACK_CLIENT_SECRET"],
    scopes=[
        "app_mentions:read",
        "chat:write",
        "files:read",
        "channels:read",
        "channels:history",
    ],
    installation_store=FileInstallationStore(base_dir="./data/slack/installations"),
    state_store=FileOAuthStateStore(
        expiration_seconds=600, base_dir="./data/slack/states"
    ),
    install_page_rendering_enabled=False,
)
app = App(signing_secret=SLACK_SIGNING_SECRET, oauth_settings=oauth_settings)

register_listeners(app)


@app.middleware
def log_request(logger, body, next):
    logger.debug(body)
    return next()


@app.event("message")
def handle_message_events(body, logger):
    logger.info(body)


flask_app = Flask(__name__)
handler = SlackRequestHandler(app)


@flask_app.route("/slack/events", methods=["POST"])
def slack_events():
    return handler.handle(request)


if __name__ == "__main__":
    log_level = os.environ.get("LOG_LEVEL", "INFO").upper()
    logging.basicConfig(level=log_level)
    # for logger_name in logging.root.manager.loggerDict:
    #     logging.getLogger(logger_name).setLevel(log_level)
    logger.info(f"Log level set to {log_level}")

    app.start(port=int(os.environ.get("PORT", 3000)))
