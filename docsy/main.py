import os
import logging

from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler
from slack_bolt.oauth.oauth_settings import OAuthSettings
from slack_sdk.oauth.installation_store import FileInstallationStore
from slack_sdk.oauth.state_store import FileOAuthStateStore


from docsy.documentation_assistant import DocumentationAssistant
from docsy.github_manager import GitHubManager

from flask import Flask, request

logger = logging.getLogger(__name__)

APP_NAME = "Docsy"
ORGANIZATION_NAME = "Laufvogel Company"

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

# Docsy uses the same GitHub App independent of who is using it
GITHUB_APP_ID = os.environ.get("GITHUB_APP_ID")
GITHUB_APP_PRIVATE_KEY = os.environ.get("GITHUB_APP_PRIVATE_KEY")


ORGANIZATION_NAME = "Laufvogel Company"

ai = DocumentationAssistant()

github = {
    # Laufvogel Company Slack
    "T0692AWNLLC": (
        51286673,
        "felixzieger/congenial-computing-machine",
        "meshcloud-docs/docs/",
    ),
    # Docsy Slack
    "T07786H8B42": (
        51663706,
        "getdocsy/docs",
        "docs/",
    ),
}


def _get_github_manager(team_id):
    github_app_installation_id, docs_repo, content_subdir = github[team_id]
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
                "accessory": {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "Yes, please"},
                    "action_id": "button_click",
                },
            }
        ],
        text=f"Hey there <@{message['user']}>! Looks like you learned something there. Should I create a PR against our public docs?",
        thread_ts=thread_ts,
    )


@app.action("button_click")
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

    logger.info(f"file_path_suggestion: {file_path_suggestion}")

    file_content = gitHubManager.get_file_content(file_path_suggestion)
    file_content_suggestion = ai.get_file_content_suggestion(
        messages, file_path_suggestion, file_content
    )

    logger.info(file_content_suggestion)
    branch_name_suggestion = ai.get_branch_name_suggestion(
        file_content, file_content_suggestion
    )

    gitHubManager.create_branch(
        file_content=file_content_suggestion,
        relative_file_path=file_path_suggestion,
        branch_name=branch_name_suggestion,
    )
    html_url = gitHubManager.create_pr(
        branch_name_suggestion,
        branch_name_suggestion,
        f"I am {APP_NAME}. I am an AI coworker at {ORGANIZATION_NAME}. I created this PR based on a slack thread. Please merge or close as you see fit!",
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
    logging.basicConfig(level=logging.DEBUG)
    app.start(port=int(os.environ.get("PORT", 3000)))
