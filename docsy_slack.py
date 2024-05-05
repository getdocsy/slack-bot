import os
import logging

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

import docsy_ai as ai
from github_manager import GitHubManager


logger = logging.getLogger(__name__)


app = App(token=os.environ.get("SLACK_BOT_TOKEN"))
gitHubManager = git.GitHubManager("felixzieger/congenial-computing-machine","felixzieger",os.environ.get("GITHUB_TOKEN"))


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
def action_button_click(body, ack, say, client, channel_id):
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
    suggestion = ai.get_suggestion(messages)
    gitHubManager.create_branch(file_content=suggestion)
    html_url = gitHubManager.create_pr("My first end-to-end test")

    url_block = {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": f"I opened a PR with that change. How does <{html_url}|this> look?",
        },
    }

    app.client.chat_postMessage(
        channel=channel_id, text="Placeholder", blocks=[url_block], thread_ts=thread_ts
    )


@app.event("message")
def handle_message_events(body, logger):
    logger.info(body)


# Start your app
if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
    logging.basicConfig(level=logging.INFO)
