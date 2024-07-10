import os
import logging

from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler
from slack_bolt.oauth.oauth_settings import OAuthSettings
from slack_sdk.oauth.installation_store import FileInstallationStore
from slack_sdk.oauth.state_store import FileOAuthStateStore


from docsy.documentation_assistant import DocumentationAssistant
from docsy.github_manager import GitHubManager
from docsy.database import Database

from flask import Flask, request

logger = logging.getLogger(__name__)

# Docsy uses OAUTH for multi-workspace slack support
SLACK_SIGNING_SECRET = os.environ.get("SLACK_SIGNING_SECRET")
oauth_settings = OAuthSettings(
    client_id=os.environ["SLACK_CLIENT_ID"],
    client_secret=os.environ["SLACK_CLIENT_SECRET"],
    scopes=["channels:read", "channels:history", "chat:write"],
    installation_store=FileInstallationStore(base_dir="./data/slack/installations"),
    state_store=FileOAuthStateStore(
        expiration_seconds=600, base_dir="./data/slack/states"
    ),
)
app = App(signing_secret=SLACK_SIGNING_SECRET, oauth_settings=oauth_settings)
ai = DocumentationAssistant()
db = Database("./data/db")


def _get_organization_context(team_id):
    customer = db.get_customer(team_id)
    return customer.organization_name


def _get_github_manager(team_id):
    customer = db.get_customer(team_id)
    github_app_installation_id = customer.github_app_installation_id
    docs_repo = customer.docs_repo
    content_subdir = customer.content_subdir

    # Docsy uses the same GitHub App independent of who is using it
    GITHUB_APP_ID = os.environ.get("GITHUB_APP_ID")
    GITHUB_APP_PRIVATE_KEY = os.environ.get("GITHUB_APP_PRIVATE_KEY")

    return GitHubManager(
        docs_repo,
        GITHUB_APP_ID,
        GITHUB_APP_PRIVATE_KEY,
        github_app_installation_id,
        content_subdir=content_subdir,
    )


@app.middleware
def log_request(logger, body, next):
    logger.debug(body)
    return next()


@app.event("app_mention")
def app_mention(message, say):
    thread_ts = message.get("thread_ts", None) or message["ts"]
    say(
        blocks=[
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"Hey there <@{message['user']}>, thanks for summoning me! Should I create a PR against our public docs?",
                },
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "Yes, please"},
                        "action_id": "button_click_yes",
                    },
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "No, thanks"},
                        "action_id": "button_click_no",
                    },
                ],
            },
        ],
        text=f"Hey there <@{message['user']}>, thanks for summoning me! Should I create a PR against our public docs?",
        thread_ts=thread_ts,
    )


@app.message("thanks")
def message_learned(message, say):
    thread_ts = message.get("thread_ts", None) or message["ts"]
    say(
        blocks=[
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"Hey there <@{message['user']}>! Looks like you learned something there. Should I create a PR against our public docs?",
                },
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "Yes, please"},
                        "action_id": "button_click_yes",
                    },
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "No, thanks"},
                        "action_id": "button_click_no",
                    },
                ],
            },
        ],
        text=f"Hey there <@{message['user']}>! Looks like you learned something there. Should I create a PR against our public docs?",
        thread_ts=thread_ts,
    )


@app.action("button_click_yes")
def action_button_click(context, body, ack, say, client, channel_id):
    ack()
    thread_ts = body["container"]["thread_ts"]
    say(
        f"All right, <@{body['user']['username']}>. I'll get back to you with a suggestion",
        thread_ts=thread_ts,
    )

    thread = client.conversations_replies(channel=channel_id, ts=thread_ts).data[
        "messages"
    ]
    messages = [
        (message["user"], message["text"])
        for message in thread
        if "user" in message and "text" in message
    ]

    gitHubManager = _get_github_manager(body["message"]["team"])
    file_paths = gitHubManager.list_md_files()
    file_path_suggestion = ai.get_file_path_suggestion(messages, file_paths)

    file_content = gitHubManager.get_file_content(file_path_suggestion)
    file_content_suggestion = ai.get_file_content_suggestion(
        messages, file_path_suggestion, file_content
    )

    branch_name_suggestion = ai.get_branch_name_suggestion(
        file_content, file_content_suggestion
    )

    gitHubManager.create_branch(
        file_content=file_content_suggestion,
        relative_file_path=file_path_suggestion,
        branch_name=branch_name_suggestion,
        commit_message=branch_name_suggestion,
    )
    organization_name = _get_organization_context(body["message"]["team"])
    html_url = gitHubManager.create_pr(
        branch_name_suggestion,
        branch_name_suggestion,
        f"I am Docsy. I am an AI coworker at {organization_name}. I created this PR based on a slack thread. Please merge or close as you see fit!",
    )

    url_block = {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": f"I opened a PR with that change. How does <{html_url}|this> look?",
        },
    }

    app.client.chat_postMessage(
        channel=channel_id,
        text="Placeholder",
        blocks=[url_block],
        thread_ts=thread_ts,
        token=context.bot_token,
    )


@app.action("button_click_no")
def action_button_click_no(body, ack, say):
    ack()
    thread_ts = body["container"]["thread_ts"]
    say(
        f"All right, <@{body['user']['username']}>. No docs for this one.",
        thread_ts=thread_ts,
    )


@app.event("message")
def handle_message_events(body, logger):
    logger.info(body)


flask_app = Flask(__name__)
handler = SlackRequestHandler(app)


@flask_app.route("/slack/events", methods=["POST"])
def slack_events():
    return handler.handle(request)


# Start your app
if __name__ == "__main__":
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    logging.basicConfig(
        level=getattr(logging, log_level, logging.INFO),
    )

    app.start(port=int(os.environ.get("PORT", 3000)))
